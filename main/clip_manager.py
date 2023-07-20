import os.path
import sys
import time
import datetime
import pickle

from pathlib import Path
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty
from config import load_param
from init_mongodb import init_db

ON_POSIX = 'posix' in sys.builtin_module_names


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


clip_handler_path = Path(__file__).parent.parent / 'recorder' / 'clip_handler.py'
clip_maker_path = Path(__file__).parent.parent / 'recorder' / 'clip_maker.py'
clip_handler = Popen('python ' + str(clip_handler_path), stdout=PIPE, bufsize=1, text=True, close_fds=ON_POSIX)
clip_maker = Popen('python ' + str(clip_maker_path), stdout=PIPE, bufsize=1, text=True, close_fds=ON_POSIX)
q_handler = Queue()
q_maker = Queue()
t_handler = Thread(target=enqueue_output, args=(clip_handler.stdout, q_handler))
t_maker = Thread(target=enqueue_output, args=(clip_maker.stdout, q_maker))
t_handler.daemon = True  # thread dies with the program
t_maker.daemon = True  # thread dies with the program
t_handler.start()
t_maker.start()

# init some parameters
db = init_db()
period = load_param('period')
gap_factor = load_param('gap_factor')
# TODO: period scaling
# timecodes[src] = [start, current, end]
timecodes_path = 'timecodes.pickle'
if os.path.exists(timecodes_path):
    timecodes = pickle_load(timecodes_path)
    timecodes = {id: timecodes[id] for id in timecodes
                 if (datetime.datetime.now() - timecodes[id][1]).total_seconds() < period * 1.1}
else:
    timecodes = {}

while True:
    # read lines without blocking
    lines_handler = []
    while True:
        try:
            lines_handler.append(q_handler.get_nowait())  # or q.get_nowait()
        except Empty:
            break
    lines_maker = []
    while True:
        try:
            lines_maker.append(q_maker.get_nowait())  # or q.get_nowait()
        except Empty:
            break

    for line_handler in lines_handler:
        train_detected = line_handler.startswith('Train detected: ')
        if train_detected or line_handler.startswith('No trains: '):
            filename = line_handler.split(': ')[1]
            src_type, src_id, src_date, src_time = filename.split('.')[0].split('-')
            src = src_type + '-' + src_id
            src_dt = datetime.datetime.strptime(f'{src_date}-{src_time}', "%y%m%d-%H%M%S")

            if train_detected:
                if src not in timecodes:
                    timecodes[src] = [src_dt, src_dt]
                    pickle_save(timecodes, timecodes_path)
                else:
                    timecodes[src][1] = src_dt
                    pickle_save(timecodes, timecodes_path)
            elif src in timecodes:
                gap = period * gap_factor
                src_start = timecodes[src][0] - datetime.timedelta(seconds=gap)
                src_end = timecodes[src][1] + datetime.timedelta(seconds=gap)
                print('\033[92m' + f'TRAIN: {src} ({src_start})-({src_end})' + '\033[0m')
                timecodes.pop(src)
                pickle_save(timecodes, timecodes_path)
                # TODO: add url; save replay
                db.trains.insert_one({"type": src_type, "yt_id": src_id, "yt_url": None,
                                      "replay_path": None, "start": src_start, "end": src_end,
                                      "railcars": None})

    for line_maker in lines_maker:
        print(line_maker, end="", flush=True)

    time.sleep(1)
