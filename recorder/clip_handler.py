import argparse
import time
import os
import sys
sys.path.append("..")

from tracker import detect_train
from config import load_param
from pathlib import Path
from ultralytics import YOLO


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', default='yolov8n_v2.pt',
                        help='model, stored in models/')
    parser.add_argument('-c', '--config', default='default.yaml',
                        help='config file to use, stored in config/')

    parser.add_argument('-o', '--record_dir', help='output dir, if None, reads from replays/clips')
    args = parser.parse_args().__dict__

    # load clip dir
    record_dir = load_param('record_dir', cfg_path=args['config'])
    if not args['record_dir']:
        if not record_dir:
            # default folder
            record_dir = Path(__file__).parent.parent / 'replays'
        else:
            # folder relative to config
            record_dir = Path(__file__).parent.parent / 'config' / record_dir
    else:
        # relative to cwd
        record_dir = Path(args['record_dir'])
    args.pop('record_dir')

    # load model
    model_filename = args.pop('model')
    model = YOLO(Path(__file__).parent.parent / 'models' / model_filename)

    # load config
    sleep_factor = load_param('sleep_factor', cfg_path=args['config'])
    period = load_param('period', cfg_path=args['config'])
    clip_age = load_param('clip_age', cfg_path=args['config'])
    if not clip_age:
        clip_age = period
    sleep_time = sleep_factor * period
    save_clips = load_param('save_clips', cfg_path=args['config'])

    while True:
        # get files sorted by date
        files = os.listdir(record_dir / 'clips')
        files.sort(key=lambda x: os.path.getmtime(record_dir / 'clips' / x))
        files = [f for f in files if time.time() - os.path.getmtime(record_dir / 'clips' / f) > clip_age]
        if files:
            to_delete = []
            to_move = []
            for file in files:
                res = detect_train(model, record_dir / 'clips' / file, show=False, verbose=False)
                if res:
                    print('Train detected:', file, flush=True)
                    if save_clips:
                        to_move.append(file)
                    else:
                        to_delete.append(file)
                else:
                    print('No trains:', file, flush=True)
                    to_delete.append(file)

            temp = to_delete.copy()
            to_delete = []
            for filename in temp:
                try:
                    os.remove(record_dir / 'clips' / filename)
                except PermissionError as e:
                    to_delete.append(filename)
                    print('\033[93m' + f"WARNING: DELETING {e}" + '\033[0m', flush=True)
            temp = to_move.copy()
            to_move = []
            for filename in temp:
                try:
                    os.rename(record_dir / 'clips' / filename, record_dir / 'train_clips' / filename)
                except PermissionError as e:
                    to_move.append(filename)
                    print('\033[93m' + f"WARNING: MOVING {e}" + '\033[0m', flush=True)
        else:
            print(f'No clips left. Sleeping for {sleep_time:.2f}s', flush=True)
            time.sleep(sleep_time)
