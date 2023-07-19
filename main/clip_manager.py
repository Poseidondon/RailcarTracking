import sys
import time

from pathlib import Path
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


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

# TODO: replace it
verbose = True
while True:
    # read lines without blocking
    line_handler = None
    try:
        line_handler = q_handler.get_nowait()  # or q.get_nowait()
    except Empty:
        pass
    line_maker = None
    try:
        line_maker = q_maker.get_nowait()  # or q.get_nowait()
    except Empty:
        pass

    if verbose:
        if line_handler:
            print("HANDLER:", line_handler, end="", flush=True)
        if line_maker:
            print("MAKER:", line_maker, end="", flush=True)

    time.sleep(1)
