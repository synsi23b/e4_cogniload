"""Example program to show how to read a multi-channel time series from LSL."""

import pylsl

# first resolve an EEG stream on the lab network
print("looking for empatica stream of gleen")
#streams = pylsl.resolve_byprop('source_id', 'gleen')
streams = pylsl.resolve_streams()

for st in streams:
    print(st.source_id())
# create a new inlet to read from the stream
inlet = pylsl.StreamInlet(streams[0])

while True:
    # get a new sample (you can also omit the timestamp part if you're not
    # interested in it)
    sample, timestamp = inlet.pull_sample()
    print(timestamp, sample)