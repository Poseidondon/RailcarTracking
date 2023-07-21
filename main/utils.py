import os.path
import pickle
import datetime
import sys

sys.path.append("..")

from pymongo import MongoClient
from config import load_param
from pathlib import Path
from subprocess import PIPE, Popen


def init_db(uri="mongodb://localhost:27017/"):
    client = MongoClient(uri)
    return client.RailcarTracking


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


def pickle_save(obj, path):
    with open(path, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def pickle_load(path):
    with open(path, 'rb') as handle:
        obj = pickle.load(handle)
    return obj


def get_dt(filename):
    return datetime.datetime.strptime('-'.join(filename.split('.')[0].split('-')[2:4]), "%y%m%d-%H%M%S")


def save_record(src: str, start: datetime.datetime, end: datetime.datetime, cfg='default.yaml', replay_dir=None):
    # get dir with replays
    if not replay_dir:
        replay_dir = load_param('record_dir', cfg)
        if replay_dir:
            replay_dir = Path(__file__).parent.parent / 'config' / load_param('record_dir', cfg)
        else:
            replay_dir = Path(__file__).parent.parent / 'replays'

    if not os.path.exists(replay_dir):
        raise FileNotFoundError("Such replay dir does not exists")

    # validate start and end
    if end < start:
        print('\033[91m' + f"ERROR: Record start time: ({start}) exceeds record end time ({end})" + '\033[0m',
              flush=True)
        raise ValueError(f"Record start time: ({start}) exceeds record end time ({end})")

    # open files
    path = replay_dir / 'records' / src
    if not os.path.exists(path):
        print('\033[93m' + f"WARNING: No records for {src} in time interval ({start})-({end})!" + '\033[0m',
              flush=True)
        return None
    files = os.listdir(path)
    # empty folder check
    if len(files) == 0:
        print('\033[93m' + f"WARNING: No records for {src} in time interval ({start})-({end})!" + '\033[0m',
              flush=True)
        return None
    files_with_dt = [(f, get_dt(f)) for f in files]
    files_with_dt.sort(key=lambda x: x[1])

    # check for suitable records
    if end < files_with_dt[0][1]:
        print('\033[93m' + f"WARNING: No records for {src} in time interval ({start})-({end})!" + '\033[0m',
              flush=True)
        return None

    first_file_ix = None
    last_file_ix = None
    for i, (f, dt) in enumerate(files_with_dt):
        if first_file_ix is None:
            if start < dt:
                first_file_ix = max(i - 1, 0)
                if i == 0:
                    print('\033[93m'+f"WARNING: No record for '{src}' at the begining ({start})!"+'\033[0m',
                          flush=True)
        if first_file_ix is not None:
            if end <= dt:
                last_file_ix = max(i - 1, 0)
                break
    if last_file_ix is None:
        print('\033[93m'+f"WARNING: No record for '{src}' at the end ({end})!"+'\033[0m',
              flush=True)
        last_file_ix = len(files_with_dt) - 1

    files = [files_with_dt[i][0] for i in range(first_file_ix, last_file_ix + 1)]
    files_formatted = '|'.join([str(replay_dir / 'records' / src / f) for f in files])
    out_path = replay_dir / 'train_replays' / (src + '-' + start.strftime("%y%m%d-%H%M%S") + '.ts')
    ffmpeg_command = f"ffmpeg -hide_banner -loglevel warning -i \"concat:{files_formatted}\" -c copy {out_path}"
    process = Popen(ffmpeg_command, stdout=PIPE)
    exit_code = process.wait()

    if exit_code == 0:
        return str(out_path)
    else:
        raise ChildProcessError("FAIL: ffmpeg concatenation failed!")
