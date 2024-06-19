
import time


def _replace_special_char(name: str, target: str):
    chars_to_replace = ['/', '\\', '.']
    for char in chars_to_replace:
        name = name.replace(char, target)
    return name

def get_timestamp():
    return int(time.time())

def fixup_job_path(job_path):
    return _replace_special_char(job_path, target="_")

def fixup_snapshotname(name: str):
    return _replace_special_char(name, target="-")
