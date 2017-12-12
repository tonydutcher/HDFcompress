#!/usr/bin/env python
import h5py
import os
from glob import glob
import numpy as np

from hdf5_process_subject import Subject
from config import config

# working on a single subject.
subject     = 'No_45' 
subject_dir = os.path.join(config.DATADIR, subject)

s = Subject(subject_dir, func_dir=config.FUNCDIR, run_prefix=config.RUNPREFIX, func_file=config.FUNCFILE_P)
s.find_runs()
s.load_runs()

# gets to the actual data.
s.hdf['func']['run_1']['data'][0]
s.hdf['func']['run_1'].attrs['trs']

# Get the data
data = list(runs_hdf[1][list(runs_hdf[0].keys())[0]])

study_vols = 'behav/pymvpa/study_vols.txt'
rest_vols  = 'behav/pymvpa/rest_vols.txt'
loc_vols   = 'behav/pymvpa/loc_stimtype_vols.txt'

# path to confound variable
confounds  = 'BOLD/functional_?/QA/confound.txt'

metadata_file   = os.path.join(SUBPATH, loc_vols)
# load file containing metadata
if not os.path.exists( metadata_file ):
    raise Exception( "Cannot find file: %s"%metadata_file )

# for processing different kinds of files
if metadata_file.endswith('.csv'):
    info = np.recfromcsv( metadata_file, delimiter=',')

elif metadata_file.endswith('.txt'):
    info = np.recfromcsv( metadata_file, delimiter='\t')

# dictionary for all volume-based labels
label = {}
for i,row in enumerate(info):
    ind = int(round(row[0]))
    if col_headers is not None and len(col_headers) != len(info.dtype.names):
        headers=col_headers
    else:
        headers=info.dtpe.names
        print "Given headers and # of columns mismatch, using specified column names"
    for col in headers:
        if col not in label:
            label[col]  = [np.nan for _ in range(self.nframes)]
        # fill in timepoint with label value
        label[col][ind] = row[col]

    # data type correction
    for key,val in label.iteritems():
        label[key] = np.array(val)

    for column in [item_label, category_label]:
        try:
            # change object id to str (after casting to int)
            is_nan = np.isnan(label[column])
            label[column] = label[column].astype(np.int).astype(np.str)
        except:
            # change object id to str
            label[column] = label[column].astype(np.str)
            is_nan = (label[column] == '') | (label[column] == 'nan')

        # create none category
        label[column][is_nan] = 'none'

    def make_set(key, ignore=[]):
        if label[key].dtype == np.number:
            items = np.unique( label[key][~np.isnan(label[key])] )
        else:
            items = np.unique( label[key] )
        return set([x for x in items if x not in ignore])

    self.object_ids = make_set(item_label, ignore=['none'])
    self.categories = make_set(category_label, ignore=['none'])
    self.exposures  = make_set(exposure_label)

    self.label = label