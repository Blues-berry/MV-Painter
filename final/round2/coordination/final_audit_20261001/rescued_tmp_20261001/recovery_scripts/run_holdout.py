import sys

sys.path.insert(0, "/4T/CXY/MV-Painter")
sys.path.insert(0, "/4T/CXY/MV-Painter/geotex")
import geotex.explore_contradiction as exp
import geotex.eval_exploration as ee
from omegaconf import OmegaConf


def stage(progress, early, middle, late):
    if progress < 1.0 / 3.0:
        return early
    if progress < 2.0 / 3.0:
        return middle
    return late


def make_schedules():
    return {
        "fixed_low": lambda p: 1.25,
        "fixed_high": lambda p: 2.50,
        "C3_TCAS": lambda p: stage(p, 1.25, 2.50, 1.25),
        "layer_LHL": lambda p: {
            "deep": stage(p, 1.25, 2.50, 1.25),
            "middle": stage(p, 1.25, 2.50, 1.25),
            "shallow": stage(p, 0.50, 0.75, 0.50),
        },
    }


exp.make_schedules = make_schedules


def load_model(config_path, checkpoint_path, device):
    return ee.load_model(config_path, checkpoint_path, device), OmegaConf.load(config_path)


exp.load_model = load_model
sys.argv = [
    "explore_contradiction.py",
    "--config", "/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/clean_holdout.yaml",
    "--checkpoint", "/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_rerun_20260928/checkpoints/geotex_step_0002000.pt",
    "--output_dir", "/4T/tmp/mvpainter-recovery-HLzm9O/scheme_new_schedule/holdout",
    "--num_objects", "276",
    "--num_steps", "50",
    "--save_maps", "0",
    "--device", "cuda:0",
]
exp.main()
