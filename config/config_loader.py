import yaml

from pathlib import Path


def load_param(param, cfg_path='default.yaml'):
    path = Path(__file__).parent / cfg_path
    cfg = yaml.load(open(path), Loader=yaml.SafeLoader)
    if param not in cfg:
        raise KeyError(f"Parameter '{param}' does not exist. See default.yaml for existing parameters.")
    else:
        return None if cfg[param] == 'None' else cfg[param]


def load_config(cfg_type: str, cfg_path='default.yaml'):
    all_configs = {'tracker': ['device', 'save', 'project', 'name', 'exist_ok', 'conf', 'iou', 'max_det', 'tracker',
                               'stream', 'persist', 'vid_stride', 'show', 'debug', 'verbose', 'line_width',
                               'show_labels', 'show_conf', 'boxes'],
                   'clipper': ['source', 'period', 'repeats', 'verbose', 'timeout_factor', 'ext', 'record_dir',
                               'duration', 'clip_fps', 'max_height'],
                   'train_detector': ['device', 'save', 'project', 'name', 'exist_ok', 'conf', 'iou', 'max_det',
                                      'tracker', 'stream', 'persist', 'vid_stride', 'show', 'verbose', 'debug',
                                      'line_width', 'show_labels', 'show_conf', 'boxes', 'tolerance', 'max_angle']}
    if cfg_type not in all_configs:
        raise KeyError(f"Config '{cfg_type}' does not exist. Available configs are {', '.join(all_configs)}.")
    else:
        # load proper args
        path = Path(__file__).parent / cfg_path
        cfg = yaml.load(open(path), Loader=yaml.SafeLoader)
        cfg = {key: cfg[key] for key in cfg if key in all_configs[cfg_type]}

        # replace 'None' with None
        cfg = {key: None if cfg[key] == 'None' else cfg[key] for key in cfg}

        return cfg
