from railcar_tracker import count_objects
from pprint import pprint

model_path = 'models/yolov8n_v2.pt'
video_path = 'video_examples/stat_4-2_720-30.mp4'
kwargs = {
    'conf': 0.6,
    'iou': 0.4,
    'tracker': 'customtrack_fast.yaml',
    'show': True,
    'line_width': 2,
    'stream': True,
    'debug': False,
    'verbose': True
}
counter, railcars = count_objects(model_path, video_path, **kwargs)
pprint(railcars)
print(counter, '\nTotal:', sum(counter.values()))
"""
Counter({'hopper': 70, 'tank': 13, 'flatcar_bulkhead': 8, 'gondola': 4, 'container': 4, 'flatcar': 2}) 
Total: 101
"""
