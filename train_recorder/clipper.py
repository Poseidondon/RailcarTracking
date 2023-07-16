from subprocess import Popen, PIPE


def youtube_clip(url, out, duration=5, fps=7, max_height=720, verbose=True):
    """
    Records last {duration} seconds of YouTube stream

    :param url: link to YouTube stream
    :param out: path for output file
    :param duration: clip duration
    :param fps: desired fps
    :param max_height: output video will not exceed this height
    :param verbose: print ffmpeg output
    :return: exit code
    """

    ytdl_command = f"""youtube-dl -f "best[height<={max_height}]" --youtube-skip-dash-manifest -g {url}"""
    process = Popen(ytdl_command, stdout=PIPE)
    output, err = process.communicate()
    exit_code = process.wait()

    if exit_code == 0:
        stream_url = output.decode().replace('\n', '')
        ffmpeg_command = f"""ffmpeg -t {duration} -an -sn -dn -i {stream_url} -filter:v fps=fps={fps} -y {out}"""
        process = Popen(ffmpeg_command, stdout=PIPE)
        output, err = process.communicate()
        exit_code = process.wait()

        if verbose:
            log = output.decode().replace('\n', '')
            print(log)

    return exit_code
