import argparse
import os.path
import sys
import time
import shutil

sys.path.append("..")

from config import load_param
from subprocess import PIPE, Popen
from clipper import get_yt_id
from pathlib import Path

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='default.yaml',
                        help='config file to use, stored in config/')
    parser.add_argument('input', type=str, help='live stream url to record')
    args = parser.parse_args().__dict__

    # loading params from config
    cfg = args.pop('config')
    max_height = load_param('max_height', cfg)
    segment_fps = load_param('segment_fps', cfg)
    segment_time = load_param('segment_time', cfg)
    segment_count = load_param('segment_count', cfg)
    record_dir = load_param('record_dir', cfg)
    if not record_dir:
        record_dir = Path(__file__).parent.parent / 'replays' / 'records'
    else:
        record_dir = Path(__file__).parent.parent / 'config' / cfg['record_dir'] / 'records'

    while True:
        # getting stream url
        ytdl_command = f"""youtube-dl -f "best[height<={max_height}]" --youtube-skip-dash-manifest -g {args['input']}"""
        process = Popen(ytdl_command, stdout=PIPE)
        output, err = process.communicate()
        exit_code = process.wait()
        if exit_code == 0:
            break
        else:
            print('\033[93m' + f"WARNING: Can't get stream url for {args['input']}!" + '\033[0m', flush=True)
            time.sleep(1)

    # reset folder
    yt_id = get_yt_id(args['input'])
    shutil.rmtree(record_dir / f"yt-{yt_id}")
    os.mkdir(record_dir / f"yt-{yt_id}")

    # download segments
    stream_url = output.decode().replace('\n', '')
    ffmpeg_command = f"ffmpeg -hide_banner -loglevel warning -an -sn -dn -i {stream_url} -filter:v"\
                     + f" fps=fps={segment_fps} -f ssegment -segment_time {segment_time} -strftime 1"\
                     + f" {record_dir}\\yt-{yt_id}\\yt-{yt_id}-%y%m%d-%H%M%S.ts"
    process = Popen(ffmpeg_command, stdout=PIPE)

    # segment cleaner
    while True:
        files = os.listdir(record_dir / f"yt-{yt_id}")
        files.sort(key=lambda x: os.path.getmtime(record_dir / f"yt-{yt_id}" / x))
        excess_files = len(files) - (segment_count + 1)
        for i in range(excess_files):
            os.remove(record_dir / f"yt-{yt_id}" / files[i])

        time.sleep(segment_time)
