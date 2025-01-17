import os
import pathlib

from helpers.config import MachineConfig

SOURCE_ROOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parents[1]
RUN_DIR = pathlib.Path(MachineConfig["run_dir"])
IMG_PATH = RUN_DIR / 'img'
RESULT_PATH = RUN_DIR / 'results'
