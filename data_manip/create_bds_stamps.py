from helper import get_participant_folders, get_sorted_bds_files
import csv
from datetime import datetime, time, timedelta

def main():
    participants = get_participant_folders()
    for part in participants:
        create_bds_stamps(part)

BDS_HEADER = ["phase", "trial_num", "bds_count", "listen_start", "listen_end", "answer_stamp", "correct"]

def create_bds_stamps(participant):
    bds_files = get_sorted_bds_files(participant)

    with open(participant / "BDS_STAMPS.csv", "w") as of:
        csvw =  csv.DictWriter(of, fieldnames=BDS_HEADER)
        csvw.writeheader()
        phase = 0
        for bdsf in bds_files:
            phase += 1
            data = extract_bds_stamps(bdsf)
            for row in data:
                row[BDS_HEADER[0]] = phase
                csvw.writerow(row)
            

def extract_bds_stamps(filepath):
    startstamp = filepath.name.split("_")[2][:10]
    startstamp = datetime.fromtimestamp(float(startstamp))
    rows = []
    with open(filepath, "r") as infile:
        csvr = csv.DictReader(infile)
        outrow = None
        for row in csvr:
            if row["key_press"] == "13":
                # answer transmitted, save this row and prepare next start
                outrow["answer_stamp"] = get_timestamp(startstamp, row)
                outrow["bds_count"] = len(row["correct"].split(","))
                outrow["correct"] = row["was_correct"]
                rows.append(outrow)
                outrow = None
            elif type(outrow) is dict:
                stamp = get_timestamp(startstamp, row)
                if "listen_start" not in outrow:
                    outrow["listen_start"] = stamp
                else:
                    outrow["listen_end"] = stamp
            elif row["stimulus"].startswith("<p>Test"):
                # next rows will be numbers and timestamps, prepare dict
                outrow = { "trial_num" : len(rows) + 1 }
    return rows
            

def get_timestamp(startstamp, row):
    secs = float(row["time_elapsed"]) / 1000
    offset = timedelta(seconds=secs)
    return (startstamp + offset).timestamp()


main()