from datetime import datetime
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from subprocess import Popen, PIPE


def get_yt_id(url):
    id = parse_qs(urlparse(url).query).get('v', [None])[0]
    if not id:
        raise KeyError("Wrong URL format. It should include 'v' parameter, containing video ID.")
    return id


def yt_clip(url, record_dir, ext='mp4', duration=5, fps=7, max_height=720, filename=None):
    """
    Records last {duration} seconds of YouTube stream

    :param url: link to YouTube stream
    :param record_dir: output dir, if None, writes to replays/records
    :param ext: output extension; if filename specified, this will have no effect
    :param duration: record duration
    :param fps: desired fps
    :param max_height: output video will not exceed this height
    :param filename: manual file naming, overrides ext
    :return: exit code
    """

    ytdl_command = f"""youtube-dl -f "best[height<={max_height}]" --youtube-skip-dash-manifest -g {url}"""
    process = Popen(ytdl_command, stdout=PIPE)
    output, err = process.communicate()
    exit_code = process.wait()

    if exit_code == 0:
        if not filename:
            yt_id = get_yt_id(url)
            filename = yt_id + '-' + datetime.now().strftime("%y%m%d-%H%M%S") + '.' + ext
        path = Path(record_dir) / 'clips' / filename

        stream_url = output.decode().replace('\n', '')
        ffmpeg_command = f"""ffmpeg -hide_banner -loglevel warning -t {duration}"""\
                         + f""" -an -sn -dn -i {stream_url} -filter:v fps=fps={fps} -y {path}"""
        process = Popen(ffmpeg_command, stdout=PIPE)
        output, err = process.communicate()
        exit_code = process.wait()

    if exit_code != 0:
        raise ChildProcessError(f"Failed to make record on {url}!")
