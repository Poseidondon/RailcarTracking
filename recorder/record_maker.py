import argparse
import time
import sys
import pandas as pd

sys.path.append("..")

from queue import Queue, Empty
from pathlib import Path
from subprocess import Popen, PIPE
from config import load_param
from threading import Thread
from main import enqueue_output

ON_POSIX = 'posix' in sys.builtin_module_names

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='default.yaml',
                        help='config file to use, stored in config/')
    args = parser.parse_args().__dict__

    # loading params from config
    cfg = args.pop('config')
    source = Path(__file__).parent.parent / 'config' / load_param('source', cfg)
    urls = pd.read_csv(source)['url'].tolist()
    print()

    # initializing threads
    yt_recorder_path = Path(__file__).parent.parent / 'recorder' / 'yt_recorder.py'
    yt_recorders = [Popen('python ' + str(yt_recorder_path) + f" {url} -c {cfg}",
                          stdout=PIPE, bufsize=1, text=True, close_fds=ON_POSIX) for url in urls]
    msg_queue = Queue()
    threads = [Thread(target=enqueue_output, args=(yt_rec.stdout, msg_queue)) for yt_rec in yt_recorders]
    for t in threads:
        t.daemon = True
        t.start()

    # fetching output from threads
    while True:
        # read lines without blocking
        lines = []
        while True:
            try:
                lines.append(msg_queue.get_nowait())  # or q.get_nowait()
            except Empty:
                break

        # printing lines
        for line in lines:
            print(line, end="", flush=True)

        time.sleep(5)
