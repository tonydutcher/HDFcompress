#!/usr/bin/env python
import h5py
import os
from glob import glob
import numpy as np

from hdf5SubjectIn import processSubject

# check for the existence of the config file. 
def load_config(config_file='config_perc.py'):
    config_path = '/home1/04635/adutcher/analysis/HDFcompress/config_files'
    assert os.path.exists( os.path.join( config_path, config_file ) )
    config_base = config_file.split('.')[0]
    return __import__(config_base)

# load in config file. 
config = load_config()

# working on a single subject.
subject   = 'No_45' 

s = processSubject(config, subject)

HDFcompress.py -config 'config_perc.py' -sid 'No_45' -type 'process'