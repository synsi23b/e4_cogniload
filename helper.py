from pathlib import Path

def get_participant_names():
    return [ str(x.name) for x in get_participant_folders()]

def get_participant_folders():
    return Path("dataset").iterdir()