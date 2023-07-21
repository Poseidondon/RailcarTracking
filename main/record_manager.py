import os.path
import sys
import time
import datetime
import argparse
import sys

sys.path.append("..")

from pathlib import Path
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty
from config import load_param
from utils import init_db, enqueue_output, pickle_load, pickle_save

ON_POSIX = 'posix' in sys.builtin_module_names

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='default.yaml',
                        help='config file to use, stored in config/')
    args = parser.parse_args().__dict__

    # loading params from config
    cfg = args.pop('config')

    # initializing threads
    clip_handler_path = Path(__file__).parent.parent / 'recorder' / 'clip_handler.py'
    clip_maker_path = Path(__file__).parent.parent / 'recorder' / 'clip_maker.py'
    clip_handler = Popen('python ' + str(clip_handler_path) + f" -c {cfg}",
                         stdout=PIPE, bufsize=1, text=True, close_fds=ON_POSIX)
    clip_maker = Popen('python ' + str(clip_maker_path) + f" -c {cfg}",
                       stdout=PIPE, bufsize=1, text=True, close_fds=ON_POSIX)
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

    # fetching output from threads
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

        # detect passing trains
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
                    db.trains.insert_one({"type": src_type, "yt_id": src_id,
                                          "replay_path": None, "start": src_start, "end": src_end,
                                          "railcars": None})

        # print clip_maker info
        for line_maker in lines_maker:
            print(line_maker, end="", flush=True)

        time.sleep(1)
