import threading
from pylsl.pylsl import StreamInlet
from helper import get_participant_names
import pylsl
from threading import Thread
import numpy as np
from scipy import signal
from collections import deque

running = True

HR_FILTER_WINDOW_LENGTH = 15

def main():
    global running
    threads = []
    for part in get_participant_names():
        streams = pylsl.resolve_byprop("source_id", part)
        t = Thread(target=collect_samples, args=(part, streams))
        t.start()
        threads.append(t)
    input("Enter anything to quit!")
    running = False
    for t in threads:
        t.join()


def collect_samples(participant, streams):
    hr_stream = None
    hr_queue = deque(maxlen=HR_FILTER_WINDOW_LENGTH)
    hr_lp_sos = signal.butter(3, 0.5, btype="lowpass", analog=False, output='sos')
    acc_stream = None
    gsr_stream = None
    for st in streams:
        if st.type() == "HR":
            hr_stream = st
        if st.type() == "ACC":
            acc_stream = st
        if st.type() == "GSR":
            gsr_stream = st
    if hr_stream is None:
        print(f"Couldnt find hr stream, stopping for participant {participant}")
        return
    if acc_stream is None:
        print(f"Couldnt find acc stream, stopping for participant {participant}")
        return
    if gsr_stream is None:
        print(f"Couldnt find gsr stream, stopping for participant {participant}")
        return

    hr_stream = pylsl.StreamInlet(hr_stream)
    acc_stream = pylsl.StreamInlet(acc_stream)
    gsr_stream = pylsl.StreamInlet(gsr_stream)
    acc_stream.open_stream()
    gsr_stream.open_stream()

    hr_last_stamp = None
    # build up small queue to run filter on
    while len(hr_queue) < HR_FILTER_WINDOW_LENGTH:
        sam, hr_last_stamp = hr_stream.pull_sample()
        hr_queue.append(sam[0])

    print("HR queue filled, running output live")
    while running:
        hrsam, hr_last_stamp = hr_stream.pull_sample()
        #time_cor = hr_stream.time_correction()
        #hr_last_stamp += time_cor  # but than we also need it at the other streams, dont do it, easy!
        hr_queue.append(hrsam[0])
        gsr =  get_last_value_before(hr_last_stamp, gsr_stream)
        acc_size = calc_acc(acc_stream)
        lp_hr = signal.sosfiltfilt(hr_lp_sos, hr_queue)[-1]
        calculate_output(hr_last_stamp, lp_hr, gsr, acc_size)


def get_last_value_before(stamp, inlet):
    samples, stamps = inlet.pull_chunk()
    if samples:
        for sm, st in reversed(list(zip(samples, stamps))):
            if st < stamp:
                return sm[0]
    return None


def calc_acc(inlet):
    samples, stamps = inlet.pull_chunk()
    if samples:
        return np.linalg.norm(samples[-1])
    return 1.0


def calculate_output(stamp, hr, gsr, acc_size):
    print(stamp, hr, gsr, acc_size)

main()