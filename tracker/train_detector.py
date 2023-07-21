import numpy as np
import sys
sys.path.append("..")

from config import load_config, load_param
from numpy.linalg import norm


def detect_train(model, video_path, config='default.yaml', **kwargs):
    """
    Detects moving trains on a video

    :param model: model object
    :param video_path: path to the video
    :param config: config name, inside of config/ folder
    :param kwargs: overrides config parameters, see tracker_cfg.yaml
    :return: Counter() object, containing counts for each class and total count
    """

    # load config
    cfg = load_config('train_detector', cfg_path=config)
    for key in kwargs:
        cfg[key] = kwargs[key]
    debug = cfg.pop('debug')
    cfg['conf'] = load_param('detector_conf', config)

    tolerance = cfg.pop('tolerance')
    max_angle = cfg.pop('max_angle')
    # trajectories[id] = [tolerance, prev_pos, unit_vector]
    trajectories = {}

    for result in model.track(video_path, **cfg):
        if result.boxes.id is None:
            continue

        centers = [((x1 + x2) / 2, (y1 + y2) / 2) for x1, y1, x2, y2 in result.boxes.xyxy.tolist()]
        ids = result.boxes.id.tolist()

        for id, center in zip(ids, centers):
            if id not in trajectories:
                trajectories[id] = [1, center, None]
            else:
                vector = (trajectories[id][1][0] - center[0], trajectories[id][1][1] - center[1])
                if max(vector) <= 0.001:
                    continue
                if not trajectories[id][2]:
                    trajectories[id][1] = center
                    trajectories[id][2] = vector
                else:
                    dot_product = np.dot(vector, trajectories[id][2])
                    angle = np.arccos(dot_product / (norm(vector) * norm(trajectories[id][2])))
                    if angle >= max_angle:
                        trajectories[id] = [1, center, None]
                    else:
                        trajectories[id] = [trajectories[id][0] + 1, center, vector]
                        if trajectories[id][0] >= tolerance:
                            # Release the process
                            model.predict()
                            if debug:
                                print(f'Train detected:\t{video_path}')
                            return True

    if debug:
        print(f'No trains:\t\t{video_path}')
    return False
