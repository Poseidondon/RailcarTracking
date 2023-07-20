import argparse
import pandas as pd
import time
import sys
sys.path.append("..")

from pathlib import Path
from multiprocessing import Process
from recorder import yt_clip
from config import load_config

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='default.yaml',
                        help='config file to use, stored in config/')

    parser.add_argument('-s', '--source', help='path to csv file, containing webcam urls')
    parser.add_argument('-p', '--period', help='make a clip each period (s)', type=float)
    parser.add_argument('-r', '--repeats', help='if not None, make clips for each url REPEATS times', type=int)
    parser.add_argument('-e', '--ext', help='clips extension')
    parser.add_argument('-o', '--record_dir', help='output dir, if None, writes to dir specified in config')
    parser.add_argument('-d', '--duration', help='clip duration (s)', type=float)
    parser.add_argument('-f', '--clip_fps', help='desired clip fps', type=int)
    parser.add_argument('--max_height', help='output video will not exceed this height', type=int)
    parser.add_argument('-v', '--verbose', help='print debug info', action='store_true')
    parser.add_argument('--silent', help='do not print debug info', action='store_true')
    parser.add_argument('--timeout_factor', help='timeout=period*timeout_factor for each process', type=float)
    args = parser.parse_args().__dict__

    # load config
    cfg = load_config('clipper', cfg_path=args.pop('config'))
    if args['verbose']:
        cfg['verbose'] = True
    if args['silent']:
        cfg['verbose'] = False
    args.pop('verbose')
    args.pop('silent')

    # load clip dir
    if not args['record_dir']:
        if not cfg['record_dir']:
            record_dir = Path(__file__).parent.parent / 'replays'
        else:
            record_dir = Path(__file__).parent.parent / 'config' / cfg['record_dir']
    else:
        record_dir = args['record_dir']
    args.pop('record_dir')
    cfg.pop('record_dir')

    if not args['source']:
        args.pop('source')
        cfg['source'] = Path(__file__).parent.parent / 'config' / cfg['source']
    for arg in args:
        if args[arg]:
            cfg[arg] = args[arg]

    # main loop
    source = cfg.pop('source')
    period = cfg.pop('period')
    repeats_left = cfg.pop('repeats')
    verbose = cfg.pop('verbose')
    timeout_factor = cfg.pop('timeout_factor')
    while repeats_left is None or repeats_left > 0:
        start = time.time()

        # read urls
        urls = pd.read_csv(source)['url'].tolist()

        # run processes
        processes = [(Process(target=yt_clip,
                              args=(url, record_dir), kwargs=cfg), url) for url in urls]
        for p, _ in processes:
            p.start()
        for p, _ in processes:
            p.join(timeout=period * timeout_factor)

        # debug info
        time_spent = time.time() - start
        if verbose:
            print('\033[92m' + f'SUCCESS: {len([ec for p, _ in processes if (ec := p.exitcode) == 0])}/{len(urls)}.\t'
                               f'TIME: {time_spent:.2f}s' + '\033[0m', flush=True)
        fails = [(p, url) for p, url in processes if p.exitcode != 0]
        for p, url in fails:
            print('\033[91m' + f'FAIL: {url}\tEXITCODE: {p.exitcode}' + '\033[0m', flush=True)

        # sleep
        time_left = period - time_spent
        if time_left > 0:
            time.sleep(time_left)
        else:
            print('\033[93m' + f"WARNING: Clip maker can't keep up! Latency is {abs(time_left):.2f}s!" + '\033[0m', flush=True)

        if repeats_left:
            repeats_left -= 1
