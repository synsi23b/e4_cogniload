
"""Example program to demonstrate how to send a multi-channel time series to
LSL."""

import random
import time
from threading import Thread
from pylsl import StreamInfo, StreamOutlet
from queue import Queue
from datetime import datetime

running = True
samplequeue = Queue()

def runner(dev, outlet):
    # first create a new stream info (here we set the name to BioSemi,
    # the content-type to EEG, 8 channels, 100 Hz, and float-valued data) The
    # last value would be the serial number of the device or some other more or
    # less locally unique identifier for the stream as far as available (you
    # could also omit it but interrupted connections wouldn't auto-recover).
    print(f"now sending data... as {dev}")
    while running:
        # make a new random 8-channel sample; this is converted into a
        # pylsl.vectorf (the data type that is expected by push_sample)
        mysample = [random.random(), random.random(), random.random(),
                    random.random(), random.random(), random.random(),
                    random.random(), random.random()]
        # now send it and wait for a bit
        #outlet.push_sample(mysample)
        samplequeue.put((dev, outlet, mysample, datetime.utcnow().timestamp()))
        time.sleep(0.7)

def make_generator(num):
    dev = f"myuid{num}"
    info = StreamInfo('BioSemi'+dev, 'EEG', 8, 100, 'float32', dev)
    # next make an outlet
    outlet = StreamOutlet(info)
    return Thread(target=runner, args=(dev, outlet))

t1 = make_generator(1)
t1.start()
t2 = make_generator(2)
t2.start()
t3 = make_generator(3)
t3.start()

try:
    while True:
        dev, out, sam, tim = samplequeue.get()
        out.push_sample(sam, tim)
        print(dev)
except:
    pass
running=False
t1.join()
t2.join()
t3.join()