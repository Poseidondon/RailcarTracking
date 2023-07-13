from railcar_tracker import count_objects

model_path = 'models/yolov8n_v2.pt'
video_path = 'video_examples/stat_4-2_720-30.mp4'

counter = count_objects(model_path, video_path)
print(counter, '\nTotal:', sum(counter.values()))
