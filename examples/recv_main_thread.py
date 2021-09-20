"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_stream
from threading import Thread

# first resolve an EEG stream on the lab network


#streams = resolve_stream('type', 'GSR')

running = True

def runner(num):
    dev = f"myuid{num}"
    print(f"looking for device {dev}..")
    streams = resolve_stream('source_id', dev)
    print(dev, streams)
    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])
    while running:
        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        sample, timestamp = inlet.pull_sample()
        print(timestamp, sample)

for x in range(1, 4):
    t = Thread(target=runner, args=(x,))
    t.start()

input("enter to kill")
running = False
t.join()

