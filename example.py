from railcar_tracker import count_objects
from pprint import pprint

model_path = 'models/yolov8n_v2.pt'
video_path = 'video_examples/stat_2-3_720-30.mp4'
kwargs = {
    'conf': 0.25,
    'iou': 0.5,
    'show': True,
    'line_width': 2,
    'stream': True,
    'debug': False,
    'verbose': True
}
counter, railcars = count_objects(model_path, video_path, **kwargs)
pprint(railcars)
print(counter)

