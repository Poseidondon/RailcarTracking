import os

from ultralytics import YOLO
from pathlib import Path
from tracker import detect_train

model_path = '../models/yolov8n_v2.pt'
model = YOLO(model_path)
video_dir = '../replays/clips/'

for filename in os.listdir(video_dir):
    res = detect_train(model, Path(video_dir) / filename, show=False, verbose=False, debug=True)
