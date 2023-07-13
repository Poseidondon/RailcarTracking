import yaml
from yaml.loader import SafeLoader
from ultralytics import YOLO
from collections import Counter


def count_objects(model_path, video_path, config='tracker_cfg.yaml', **kwargs):
    """
    Count objects on video, using unique IDs

    :param model_path: path to the model
    :param video_path: path to the video
    :param config: config name, inside of config/ folder
    :param kwargs: overrides config parameters, see tracker_cfg.yaml
    :return: Counter() object, containing counts for each class and total count
    """

    # load a model
    model = YOLO(model_path)

    # tracking
    railcars = {}

    # load config
    cfg = yaml.load(open(f'config/{config}'), Loader=SafeLoader)
    for key in kwargs:
        cfg[key] = kwargs[key]
    debug = cfg.pop('debug')

    for result in model.track(video_path, **cfg):
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

    return counter
