# Railcar Tracking
Railcar Tracking is a framework to monitor railroad webcams from multiple sources.
When moving train is detected, railcars are counted and classified and replay of passing train is saved.

## Requirements
- [ffmpeg](https://ffmpeg.org/download.html)
- [youtube-dl](https://github.com/ytdl-org/youtube-dl)
- [Python>=3.4](https://www.python.org/downloads/)
- [requirements.txt](requirements.txt)

## Installing
Make sure you add [ffmpeg](https://ffmpeg.org/download.html) and [youtube-dl](https://github.com/ytdl-org/youtube-dl) to system path.
Don't forget to install [requirements.txt](requirements.txt).

## Railcar Tracker
Railcar Tracker is a tool to count railcars and classify them.

### Usage
[track_example.py](examples/track_example.py)
```python
from ultralytics import YOLO
from railcar_tracker.object_counter import count_objects

model_path = '../models/yolov8n_v2.pt'
model = YOLO(model_path)
video_path = '../video_examples/stat_1-1_720-30.mp4'

# see tracker_cfg.yaml for all kwargs
counter = count_objects(model, video_path, verbose=True)
print(counter, '\nTotal:', sum(counter.values()))
```

### Detection and Tracking
![text](static/stat_1-1_720-30.gif)

### Result
```python
Counter({'boxcar': 48, 'tank': 29, 'hopper': 7, 'gondola': 5, 'locomotive': 3}) 
Total: 92
```

### Tracker Config
You can use custom config for tracking, if it's inside `config\`:
```python
counter = count_objects(model, video_path, config='custom_tracker_cfg.yaml')
```
Default config is [tracker_cfg.yaml](config/tracker_cfg.yaml)
```yaml
# Settings for tracker and object detection
# You can also use parameters listed in https://docs.ultralytics.com/modes/predict/#inference-arguments

# General settings
device: None    # device to run on, i.e. cuda device=0/1/2/3 or device=cpu
save: False    # save video with results

# Object detection settings
conf: 0.6    # object confidence threshold for detection
iou: 0.4    # intersection over union (IoU) threshold for NMS
max_det: 300    # maximum number of detections per frame

# Tracker settings
tracker: custom_fast.yaml    # tracker config, see ultralytics/tracker/cfg
stream: True    # whether the input source is a video stream
persist: False    # whether to persist the trackers if they already exist
vid_stride: 1    # video frame-rate stride

# Debug settings
show: True    # stream output during inference
debug: False    # print counter debug info
verbose: True    # whether the inference is verbose or not

# Show settings
line_width: 2    # the line width of the bounding boxes, if None, it is scaled to the image size
show_labels: True    # show box labels
show_conf: True    # show confidence score
boxes: True    # show boxes in segmentation predictions
```

## Clipper
Clipper is a tool to save short clips of YouTube and RTSP streams.
Those clips are used to detect moving trains.

### Usage
[track_example.py](examples/track_example.py)
```python
from train_recorder.clipper import youtube_clip

youtube_clip('https://www.youtube.com/watch?v=Q9_jZVECcjY', out='../replays/clips/example.mp4',
             duration=5, fps=7, max_height=720, verbose=True)
```
### Result
[example.mp4](replays/clips/example.mp4), containing last 5 seconds of YouTube stream with 7 fps and 1280x720 size.

## Dataset
TODO

## Models
TODO
