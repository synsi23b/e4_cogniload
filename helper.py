from pathlib import Path

def get_participant_names():
    return [ str(x.name) for x in get_participant_folders()]

def get_participant_folders():
    return Path("dataset").iterdir()

def get_sorted_bds_files(particpant_path):
    files = list(particpant_path.glob("BDS_*_*.csv"))
    files = sorted(files, key=lambda x: str(x.name))
    return files