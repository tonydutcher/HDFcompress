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
    meta_dir=config.METADIR, 
    verbose=True)





def file_check( group, file):
    fname = os.path.join( group, file )
    if not os.path.exists(fname):
        raise Exception("Cannot find volume: %s"%fname)
    return fname

def read_metafile(filename, columns=0):
    """ Reads in contents of meta data file
    INPUT:
    filename - name of the file, assumed to be in meta directory
    skiprow  - 0 if no headers, 1 if headers in file """
columns = []
filename = config.REST
skiprow = 0
head = skiprow

# checks file exists 
file = file_check(s.meta_dir, filename)

# separates file type and string name of file.
fileparts = os.path.basename( file ).split('.')
if len( fileparts ) != 2:
    raise Exception("Error processing file: %s, too many . in filebase"%file)
basefile  = fileparts[0]
filetype  = fileparts[1]

# now we can load in the file.
if filetype == 'csv':
    info = np.recfromcsv( file, names=['a', 'b'], delimiter=',' )

elif filetype == 'txt':
    info = np.recfromcsv( file, names=['a', 'b'], delimiter='\t' )

else:
    logger.exception( "%s, ends in something other than .txt or .csv, we're not there yet..."%filename)

# checks that the length of the info file is the same length as the number of TRs. 
if len( info ) != (s.n_TRs-1):
    raise Exception( "Length of %s, does not number of TRs across all functional scans."%filename )
        if 'r_ind' not in s.hdf['func'][i].attrs:
        logger.exception('Run specific index not found for %s' % i)

# cycle through each run
for i,r in s.hdf['func'].iteritems():
    tr_vector = []
    run = s.hdf['func'][i].attrs['run']
    for j in s.hdf['func'][i].attrs['f_ind']:
        tr_vector.append( info[j][1] )
    s.hdf['func'][i].attrs[basefile] = np.array( tr_vector )
 

 print 'HDF5 index and meta file index disagree for %s'% file



    print s.hdf['func'][i].attrs['f_ind']
        



    s.hdf['func'][i].attrs['b_ind'] = np.array( s.hdf['func'][i].attrs['b_ind'] )


for tr,meta in enumerate(info):
    row = int(round(row[0]))










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

# load file containing metadata
if not os.path.exists( metadata_file ):
    raise Exception( "Cannot find file: %s"%metadata_file )

# for processing different kinds of files
if metadata_file.endswith('.csv'):
    info = np.recfromcsv( file, skiprow=skiprow, delimiter=',' )

elif metadata_file.endswith('.txt'):
    info = np.recfromcsv( file, skiprow=skiprow, delimiter='\t' )

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