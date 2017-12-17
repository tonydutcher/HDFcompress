#!/usr/bin/env python
import os
from glob import glob
import numpy as np
import h5py
import argparser

from config import config
from hdf5SubjectIn import Subject
#from hdf5SubjectOut import Subject

# in presentation talk about...
# 1) argparser
# 2) logging
# 3) validation

# working on a single subject.
subject   = 'No_45' 
study_dir = os.path.join(config.DATADIR, config.STUDY)
log_level = 10

def main():

s = Subject(study_dir, subject, 
    anat_dir=config.ANATDIR, 
    func_dir=config.FUNCDIR, 
    run_prefix=config.RUNPREFIX, 
    func_file=config.FUNCFILE_P, 
    meta_dir=config.METADIR,
    log_level=log_level)

s.process_metadata(config.REST)
s.process_metadata(config.LOCALIZER)
s.process_metadata(config.TASK)

if __name__ == '__main__':
    main()