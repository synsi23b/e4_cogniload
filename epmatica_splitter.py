import csv
from datetime import datetime, time, timedelta
import os, re, zipfile, shutil
from pathlib import Path
import pytz
from dateutil import parser

participants = {}
with open("score_and_help_indicator.csv", "r") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    for line in reader:
        participants[line['name']] = line

partilist = []
for i, v in enumerate(participants.keys()):
    partilist.append(v)
    print(f"{i}.\t{v}")
select = partilist[int(input("Select who to split the dataset for (number): "))]

x = str()
# search for rows that start with the same name as the selected as a base string
to_create = [ n for n in partilist if n.startswith(select) ]
to_create.remove(select)
print("Creating splitted empaticas for ", to_create)

cwddir = os.getcwd()
inzip = Path(cwddir) / "input" / participants[select]["session"]
#indir = os.path.join(cwddir, "input")
wrkdir = os.path.join(cwddir, "wrkdir")
outdir = os.path.join(cwddir, "dataset")
outdirs = [ Path(outdir) /  x for x in to_create ]
print("Using the file: ", inzip, "Unzipping...")

zipname = inzip.stem
zipfolder = os.path.join(wrkdir, zipname)
zipref = zipfile.ZipFile(inzip, 'r')
zipref.extractall(zipfolder)
zipref.close()

for off in outdirs:
    if off.is_dir():
        print("Deleting previous folder: ", off)
        shutil.rmtree(off)
    os.mkdir(off)

    last_phase = 0
    parti_data = participants[off.name]
    for phase in range(1,7):
        pt = parti_data[f"{phase}f"]
        if pt is not "":
            last_phase = phase
            phase_time = pt
    

    guy_tz = pytz.timezone(parti_data["timezone"])
    phase_date = parti_data["date"]
    phase_time = parser.parse(f"{phase_date} {phase_time}")
    phase_time = guy_tz.localize(phase_time)
    phase_time = phase_time.astimezone(pytz.UTC)
    
    
    once = True
    for filename in ["EDA.csv", "HR.csv", "ACC.csv"]:
        inputfile = os.path.join(zipfolder, filename)
        with open(inputfile, "r") as f:
            csvr = csv.reader(f)
            stamp = next(csvr)
            rate = next(csvr)
            data = [row for row in csvr]
        stamp_s = datetime.fromtimestamp(float(stamp[0]), tz=pytz.UTC)
        #stamp_s = pytz.UTC.localize(stamp_s)
        stamp_e = phase_time + timedelta(minutes=5)
        if once:
            once = False
            print("Original phase start is ", stamp_s)
            print("Generating files until phase ", last_phase, " with date ", stamp_e)
        
        delta = stamp_e - stamp_s
        data_end = int(delta.total_seconds() * int(float(rate[0])))

        outfile = off/ filename
        with open(outfile, "w") as f:
            csvw = csv.writer(f)
            csvw.writerow(stamp)
            csvw.writerow(rate)
            csvw.writerows(data[ : data_end])
        
    pass

