import yaml
from yaml.loader import SafeLoader
from collections import Counter
from pathlib import Path


def count_objects(model, video_path, config='tracker_cfg.yaml', **kwargs):
    """
    Count objects on video, using unique IDs

    :param model: model object
    :param video_path: path to the video
    :param config: config name, inside of config/ folder
    :param kwargs: overrides config parameters, see tracker_cfg.yaml
    :return: Counter() object, containing counts for each class and total count
    """

    # tracking
    railcars = {}

    # load config
    path = Path(__file__).parent.parent / 'config' / config
    cfg = yaml.load(open(path), Loader=SafeLoader)
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
