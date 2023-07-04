from ultralytics import YOLO
from collections import Counter


def count_objects(model_path, video_path, debug=False, **kwargs):
    # Load a model
    model = YOLO(model_path)

    # Track with the model
    railcars = {}

    for result in model.track(video_path, **kwargs):
        if result.boxes.id is not None:
            ids, classes, confs = result.boxes.id.tolist(), result.boxes.cls.tolist(), result.boxes.conf.tolist()
            if debug:
                print(ids, classes, confs)
            for id, cls, conf in zip(ids, classes, confs):
                if id not in railcars:
                    railcars[id] = cls, conf
                else:
                    if conf > railcars[id][1]:
                        railcars[id] = cls, conf

    counter = Counter([model.names[i[0]] for i in railcars.values()])

    return counter, railcars
