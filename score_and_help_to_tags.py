import csv
import datetime as dt
from dateutil import tz, parser
import pytz

parti = input("Enter participant name to generate tags for: ")
print(f"Generating for {parti}")

base_date = "2021-09-08 {}"

myguy = None

with open("score_and_help_indicator.csv", "r") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    for line in reader:
        if line['\ufeffname'] == parti:
            myguy = line
            break

if myguy is None:
    print("Guy not found in score_help file!")
    exit(-1)

outlines = []
for i in range(7):
    if i == 0:
        phase_base = "relax_"
    else:
        phase_base = str(i)
    phase_a =  base_date.format(myguy[phase_base + "s"])
    phase_b =  base_date.format(myguy[phase_base + "f"])
    outlines.append(phase_a)
    outlines.append(phase_b)


GER = pytz.timezone('Europe/Berlin')

outlines = [ parser.parse(x) for x in outlines ]
outlines = [ GER.localize(x) for x in outlines ]
outlines = [ x.astimezone(pytz.UTC) for x in outlines ]
outlines = [ f"{x.timestamp()}\n" for x in outlines ]

with open(f"./dataset/{parti}/tags.csv", "w") as f:
    f.writelines(outlines)
