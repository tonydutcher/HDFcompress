#!/usr/bin/env python
import h5py
import os
from glob import glob
import numpy as np

from hdf5Subject import Subject
from config import config

# working on a single subject.
subject   = 'No_45' 
study_dir = os.path.join(config.DATADIR, config.STUDY)

s = Subject(study_dir, subject, 
    anat_dir=config.ANATDIR, 
    func_dir=config.FUNCDIR, 
    run_prefix=config.RUNPREFIX, 
    func_file=config.FUNCFILE_P, 
    meta_dir=config.METADIR )

s.process_metadata(config.REST)
s.process_metadata(config.LOCALIZER)
s.process_metadata(config.TASK)