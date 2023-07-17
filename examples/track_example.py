from ultralytics import YOLO
from railcar_tracker import count_objects

model_path = '../models/yolov8n_v2.pt'
model = YOLO(model_path)
video_path = '../replays/clips/example.mp4'

# see tracker_cfg.yaml for all parameters
counter = count_objects(model, video_path, verbose=True)
print(counter, '\nTotal:', sum(counter.values()))
