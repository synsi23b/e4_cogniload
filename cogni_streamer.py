import threading
#from pylsl.pylsl import StreamInlet, StreamInfo
from helper import get_participant_names
import pylsl
from threading import Thread
import numpy as np
from scipy import signal
from collections import deque
import model_loader

running = True
GSR_LP_FILTER_WINDOW_LENGTH = 32 # 8 seconds
# this is an arbitrary threshold for how much the Accelerometer can shake before
# disregarding the samples taken. Have to set a reasonable value here
ACC_MAX = 32

# looking for streams of these participants only
# LSL stream source ID has to match these IDs
participants = [
    "inno9",
    "inno11",
    "inno12"
]


def main():
    global running
    model_loader.load_model()
    threads = []
    for part in participants:
        t = Thread(target=collect_samples, args=(part,))
        t.start()
        threads.append(t)
    input("Enter anything to quit!")
    running = False
    for t in threads:
        t.join()


def collect_samples(participant):
    sub_group = model_loader.get_subject_group(participant)
    if sub_group is None:
        info_msg(participant, "Sub ID not found in loaded model? Not trained?")
        return
    
    hr_stream = None
    acc_stream = None
    gsr_stream = None
    gsr_queue = deque(maxlen=GSR_LP_FILTER_WINDOW_LENGTH)
    gsr_lp_sos = signal.butter(3, 0.5, btype="lowpass", analog=False, output='sos', fs=4.0)

    while running:
        info_msg(participant, "Looking for LSL streams")
        streams = pylsl.resolve_byprop("source_id", participant)
        for st in streams:
            if st.type() == "HR":
                hr_stream = st
            if st.type() == "ACC":
                acc_stream = st
            if st.type() == "GSR":
                gsr_stream = st
        if hr_stream is None:
            info_msg(participant, "Couldnt find hr stream")
            continue
        if acc_stream is None:
            info_msg(participant, "Couldnt find acc stream")
            continue
        if gsr_stream is None:
            info_msg(participant, "Couldnt find gsr stream")
            continue
        break

    cogni_info = pylsl.StreamInfo(f"Cogniload {participant}", "COGNI", 1, 1.0, "float32", participant)
    outlet = pylsl.StreamOutlet(cogni_info)

    hr_stream = pylsl.StreamInlet(hr_stream)
    acc_stream = pylsl.StreamInlet(acc_stream)
    gsr_stream = pylsl.StreamInlet(gsr_stream)
    
    hr_stream.open_stream()
    acc_stream.open_stream()
    gsr_stream.open_stream()
    # get first heart rate sample, whenever that might come
    hrsam, hr_last_stamp = hr_stream.pull_sample()

    # build up small queue to run filter on
    gsr_last_stamp = None
    while len(gsr_queue) < GSR_LP_FILTER_WINDOW_LENGTH:
        samples, gsr_last_stamps = gsr_stream.pull_chunk(timeout=1)
        if samples:
            gsr_last_stamp = gsr_last_stamps[-1]
            for sam in samples:
                gsr_queue.append(sam[0])

    print("GSR queue filled, running output live")
    prev_load = 0.0
    while running:
        # pull all hr samples -> retun instant even without sample if none is buffered
        hr_new, hr_stamp_new = pull_chunk_no_throw(participant, "HR", hr_stream, timeout=0.0)
        if hr_new:
            hrsam, hr_last_stamp = hr_new[-1][0], hr_stamp_new[-1]
        #time_cor = hr_stream.time_correction()
        #hr_last_stamp += time_cor  # but than we also need it at the other streams, dont do it, easy!
        
        # pull gsr samples and refresh fifo buffer
        samples, stamps = pull_chunk_no_throw(participant, "GSR", gsr_stream, timeout=1.0)
        if samples:
            gsr_last_stamp = stamps[-1]
            for sam in samples:
                gsr_queue.append(sam[0])
        else:
            info_msg(participant, "No EDA -> skipping one round.")
            continue
        
        # calculate size of ACC to determine if the data right now is unreliable anyway
        acc_size = calc_acc(participant, acc_stream)
        if acc_size > ACC_MAX:
            info_msg(participant, f"skipped because ACC! {acc_size}. Transmitting previous value")
            outlet.push_sample([prev_load], hr_last_stamp)
            continue
        # finally try to calculate cognikload every second
        # start by low pass filtering the last few seconds of HR
        lp_gsr = signal.sosfiltfilt(gsr_lp_sos, gsr_queue)[-1]
        # than just call the model
        prev_load = model_loader.predict(sub_group, lp_gsr, hrsam)
        outlet.push_sample([prev_load], gsr_last_stamp)


def info_msg(part, msg):
    print(f"{part}: {msg}")


def pull_chunk_no_throw(part, str_type, stream, timeout):
    samples, stamps = [], []
    try:
        samples, stamps = stream.pull_chunk(timeout=timeout)
    except pylsl.LostError:
        info_msg(part, f"Lost {str_type} stream")
    return samples, stamps

# def get_last_value_before(stamp, inlet):
#     samples, stamps = inlet.pull_chunk()
#     if samples:
#         for sm, st in reversed(list(zip(samples, stamps))):
#             if st < stamp:
#                 return sm[0]
#     return None

def calc_acc(part, inlet):
    try:
        samples, stamps = inlet.pull_chunk()
        if samples:
            veclength = np.linalg.norm(samples[-1])
            return abs(veclength - 64)
    except pylsl.LostError:
        info_msg(part, "Lost ACC stream")
    return 0.0


main()