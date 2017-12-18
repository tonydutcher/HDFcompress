#!/usr/bin/env python
import os
from glob import glob
import numpy as np
import h5py
import argparse

from hdf5SubjectIn import processSubject
#from hdf5SubjectOut import Subject

description="This function processes nifti and text files into HDF5 format and \
             also takes HDF5 format data (processed by this function) and outputs \
             it back into original nifti and text file format \
             - see https://github.com/tonydutcher/HDFcompress for details on the implementation"

# argparser
parser = argparse.ArgumentParser(description=description)
parser.add_argument("-config,", metavar="config-file", action="store", dest="config_file", type=str, required=True, help=("The name of the config file - this must be filled out and exist in the config_file directory in the source directory.") )
parser.add_argument("-sid,", metavar="subject-id", action="store", dest="subject", type=str, required=True, help=("The id of the subject - one level below 'study' and top-level for subject.") )
parser.add_argument("-type,", metavar="analyze-type", action="store", dest="atype", type=str, required=True, help=("Input: 'process' or 'create', process = data to hdf5, create = hdf5 back to data") )
parser.add_argument("-logs", metavar="log-level", action="store", dest="log_level", type=int, required=False, default=10, help=("The level logging, default 10 - see python's logging module - "))
args = parser.parse_args()

# asserts the variable type for variable atype
assert (args.atype=='process' or args.atype=='create')

# check for the existence of the config file. 
def load_config(config_file=args.config_file):
    config_path = '/home1/04635/adutcher/analysis/HDFcompress/config_files'
    assert os.path.exists( os.path.join( config_path, config_file ) )
    config_base = config_file.split('.')[0]
    return __import__(config_base)

# load in config file. 
config = load_config()

# run analysis on a single subject. 
def run_subject( atype, config, subject, log_level ):
    """ Function to run either process or create subject. """

    # checks for atype variable type.
    if atype == 'process':
        print "Running process subject."
        s = processSubject(config, subject, log_level)

    else:
        print "Running create subject."
        pass

# runs things. 
run_subject(args.atype, config, args.subject, args.log_level)