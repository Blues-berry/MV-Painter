"""Run the frozen main-adapter trainer with an explicit, recorded seed."""
import random
import runpy
import sys
from pathlib import Path

import numpy as np
import torch

TRAIN_ENTRY = Path('/tmp/mv_main_rerun/geotex/train.py')
CONFIG = Path('/4T/CXY/MV-Painter/final/round2/main_adapter_original276_leaveout_20261012/training_config.yaml')
OUTPUT = Path('/4T/CXY/MV-Painter/mvpoutput/reviewer1_main_original276_leaveout_20261012')
SEED = 20261012
device = sys.argv[1] if len(sys.argv) > 1 else 'cuda:0'

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

sys.argv = [
    str(TRAIN_ENTRY), '--config', str(CONFIG), '--output_dir', str(OUTPUT),
    '--steps', '2000', '--save_every', '500', '--lr', '1e-4', '--device', device,
]
runpy.run_path(str(TRAIN_ENTRY), run_name='__main__')
