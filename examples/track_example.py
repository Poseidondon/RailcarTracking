from ultralytics import YOLO
from railcar_tracker.object_counter import count_objects

model_path = '../models/yolov8n_v2.pt'
model = YOLO(model_path)
video_path = '../video_examples/stat_1-1_720-30.mp4'

# see tracker_cfg.yaml for all parameters
counter = count_objects(model, video_path, verbose=True)
print(counter, '\nTotal:', sum(counter.values()))
