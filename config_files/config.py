#!/usr/bin/env python
import os

# need to assert that this file exists
CONFIG_PATH = '/Users/anthonydutcher/analysis/cs380/project/HDFcompress/config_files'
CONFIG_FILE = 'config_perc.py'
FULL_FILE_PATH = os.path.join(CONFIG_PATH, CONFIG_FILE)
assert os.path.exists(FULL_FILE_PATH)

def load_config(config_file=CONFIG_FILE):
    config_base = config_file.split('.')[0]
    return __import__(config_base)

config = load_config()