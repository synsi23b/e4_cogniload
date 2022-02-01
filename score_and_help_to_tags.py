import csv
import datetime as dt
from tkinter.messagebox import NO
from dateutil import tz, parser
import pytz

parti = input("Enter participant name to generate tags for: ")
print(f"Generating for {parti}")


myguy = None

with open("score_and_help_indicator.csv", "r") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    for line in reader:
        if line['name'] == parti:
            myguy = line
            break



if myguy is None:
    print("Guy not found in score_help file!")
    exit(-1)

base_date = myguy["date"] + " {}"
outlines = []
for i in range(7):
    if i == 0:
        phase_base = "relax_"
    else:
        phase_base = str(i)
    phase_a_time = myguy.get(phase_base + "s", None)
    if phase_a_time is None:
        print("Stopping time generation at Phase {i} -> not populated")
        break
    phase_a =  base_date.format(phase_a_time)
    phase_b =  base_date.format(myguy[phase_base + "f"])
    outlines.append(phase_a)
    outlines.append(phase_b)


guy_tz = pytz.timezone(myguy["timezone"])
print(f"Timezone for score_and_help_indicator_times is set to {guy_tz.tzname(None)}")

outlines = [ parser.parse(x) for x in outlines ]
outlines = [ guy_tz.localize(x) for x in outlines ]
outlines = [ x.astimezone(pytz.UTC) for x in outlines ]
outlines = [ f"{x.timestamp()}\n" for x in outlines ]

with open(f"./dataset/{parti}/tags.csv", "w") as f:
    f.writelines(outlines)
