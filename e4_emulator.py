import pylsl
from helper import get_participant_folders
from threading import Thread
from time import sleep
from datetime import datetime


# filename, channels, type, start_offset
# heartrate starts 10 seconds after the others, so just ignore
# first 10 seconds of the other files
datafiles = [
  ("ACC.csv", 3, "ACC", 10),
  ("EDA.csv", 1, "GSR", 10),
  ("HR.csv", 1, "HR", 0)
]

running = True

looking_for_part = [
    "inno9",
]

def main():
    threads = []
    for participant in get_participant_folders():
        if participant.name not in looking_for_part:
            print(f"skipping {participant}")
            continue
        print(f"starting {participant}")
        for file, channel, type, offset in datafiles:
            t = Thread(target=start_stream, args=(participant / file, channel, type, offset, datetime.utcnow().timestamp()))
            threads.append(t)
            t.start()
    sleep(2.0)
    input("Enter something to stop streaming")
    global running
    running = False
    for t in threads:
        t.join()

def start_stream(file, channel, type, offset, starttime):
    print(f"Starting stream of {file}")
    with open(file, "r") as infile:
        startstamp = infile.readline()
        rate = float(infile.readline().rstrip().split(",")[0])
        sleeptime = 1 / rate

        skiplines = round(rate * offset)
        lines = infile.readlines()[skiplines:]

        print(f"Opening stream source id: {file.parent.name}, type: {type}")
        sinfo = pylsl.StreamInfo(f"E4emu", type, channel, rate, "float32", str(file.parent.name))
        outlet = pylsl.StreamOutlet(sinfo)
        if channel == 1:
            for l in lines:
                outlet.push_sample([float(l)], starttime)
                starttime += sleeptime
                sleep(sleeptime)
                if not running:
                    break
        elif channel == 3:
            for l in lines:
                outlet.push_sample([float(x) for x in l.split(",")], starttime)
                starttime += sleeptime
                sleep(sleeptime)
                if not running:
                    break
    print(f"Stream done of file {file}")


main()