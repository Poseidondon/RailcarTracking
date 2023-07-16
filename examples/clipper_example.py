from train_recorder.clipper import youtube_clip

youtube_clip('https://www.youtube.com/watch?v=Q9_jZVECcjY', out='../replays/clips/example.mp4',
             duration=5, fps=7, max_height=720, verbose=True)
