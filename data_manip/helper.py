from pathlib import Path
from datetime import datetime
from csv import DictReader
from sqlite3 import Timestamp


def get_participant_names():
    return [ str(x.name) for x in get_participant_folders()]

def get_participant_folders():
    return Path("dataset").iterdir()

def get_sorted_bds_files(particpant_path):
    files = list(particpant_path.glob("BDS_*_*.csv"))
    files = sorted(files, key=lambda x: str(x.name))
    return files

def get_participant_eda(participant_folder):
    with open(participant_folder / "EDA.csv") as f:
        dt = datetime.fromtimestamp(float(f.readline()))
        freq = float(f.readline())
        data = [ float(x) for x in f.readlines() ]
    return (dt, freq, data)

def get_participant_bds_stamps(participant_folder):
    with open(participant_folder / "BDS_STAMPS.csv") as f:
        dr = DictReader(f)
        fieldnames = dr.fieldnames
        data = [ x for x in dr ]
        for row in data:
            row["listen_start"] = datetime.fromtimestamp(float(row["listen_start"]))
            row["listen_end"] = datetime.fromtimestamp(float(row["listen_end"]))
            row["answer_stamp"] = datetime.fromtimestamp(float(row["answer_stamp"]))
    return data

if __name__ == "__main__":
    print(list(get_participant_folders()))