#!/usr/bin/env python
import os
from glob import glob

import h5py
import numpy as np
import nibabel as nb

from config import config

class Subject(object):
    def __init__(self, subject_dir, func_dir=config.FUNCDIR, run_prefix=None, func_file=config.FUNCFILE_P):
        self.subject_dir = subject_dir
        self.func_dir    = os.path.join( subject_dir, func_dir )
        self.run_prefix  = run_prefix
        self.func_file   = func_file

        # create a subject .hdf5 to insert things into.
        self.hdf = h5py.File('%s.hdf5'%self.subject_dir,'w')

    ## Read in functional brains into hdf5 format.
    # find runs based on some user input.
    def find_runs(self, nb_load=True):
        print "finding runs..."
        match_this = os.path.join(self.func_dir, self.run_prefix+'*' )
        run_dirs   = [ d for d in glob(match_this) if os.path.isdir(d) ]
        ordering   = sorted( [ int(os.path.basename(r).split('_')[-1]) for r in run_dirs ] )
        sorted_run_dirs = [ os.path.join(self.func_dir, self.run_prefix+str(i)) for i in ordering ]

        print "found: ", run_dirs
        # load all runs
        runs = []
        for run in sorted_run_dirs:
            fname = self.run_volume(run)
            print "including vol: %s"%fname
            # load nifti
            if nb_load:
                img = nb.load(fname)
                runs.append(img)
            else:
                runs.append(fname)
        # save a 
        self.runs = runs

    def run_volume(self, run_dir):
        fname = os.path.join(run_dir, self.func_file)
        if not os.path.exists(fname):
            raise Exception("Cannot find volume: %s"%fname)
        return fname

    # load in runs, gathering information about the data.
    def load_runs(self, combined=True):
        print "loading data and preprocessing (if necessary)..."
        runs_hdf=[]
        self.func = self.hdf.create_group("func")
        self.func.attrs['n_runs'] = len(self.runs)

        for i,r in enumerate( self.runs ):
            runs_hdf.append( self.func.create_group( "run_%s"%(int(i)+1) ) )
            rdat     = runs_hdf[i].create_dataset( "data", data=r.get_data() )
            hdr      = r.get_header()
            for k,v in hdr.items():
                runs_hdf[i].attrs["nifti1_" + k] = v
            runs_hdf[i].attrs['nifti1_affine'] = r.get_affine()
            runs_hdf[i].attrs['trs'] = r.get_data().shape[-1]
            runs_hdf[i].attrs['run'] = i+1
            runs_hdf[i].attrs['r_ind'] = np.arange(0,r.get_data().shape[-1])

    def combine_runs(self):
        arr = []
        all_trs = sum( [ self.hdf['func']['run_'+str(i)]['data'][0].shape[-1] for i in np.arange(1,self.func.attrs['n_runs']+1) ] )
        for i in np.arange(1,self.func.attrs['n_runs']+1):
            data = self.hdf['func']['run_'+str(i)]['data'][:]
            n_voxels = np.prod(data.shape[:-1])
            arr.append( data.reshape( n_voxels, data.shape[-1]) )

        np.concatenate( arr )





# def load_metadata(self, metadata_file ):
#     print "loading metadata..."

#     # load file containing metadata
#     if not os.path.exists( metadata_file ):
#         raise Exception( "Cannot find file: %s"%metadata_file )
    
#     # for processing different kinds of files
#     if metadata_file.endswith('.csv'):
#         info = np.recfromcsv( metadata_file, delimiter=',')

#     elif metadata_file.endswith('.txt'):
#         info = np.recfromcsv( metadata_file, delimiter='\t')

#     # dictionary for all volume-based labels
#     label = {}

#     # align labels with volume shape
#     for i,row in enumerate(info):
#         ind = int(round(row[onset_col]))

#         # if timepoint is outside of the current scope, skip.
#         if ind > self.nframes -1: continue

#         # save all columns
#         for col in self.info.dtype.names:
#             # initialize if col doesn't exist
#             if col not in label:
#                 label[col]  = [np.nan for _ in range(self.nframes)]
#             # fill in timepoint with label value
#             label[col][ind] = row[col]

#     # data type correction
#     for key,val in label.iteritems():
#         label[key] = np.array(val)

#     for column in [item_label, category_label]:
#         try:
#             # change object id to str (after casting to int)
#             is_nan = np.isnan(label[column])
#             label[column] = label[column].astype(np.int).astype(np.str)
#         except:
#             # change object id to str
#             label[column] = label[column].astype(np.str)
#             is_nan = (label[column] == '') | (label[column] == 'nan')

#         # create none category
#         label[column][is_nan] = 'none'

#     def make_set(key, ignore=[]):
#         if label[key].dtype == np.number:
#             items = np.unique( label[key][~np.isnan(label[key])] )
#         else:
#             items = np.unique( label[key] )
#         return set([x for x in items if x not in ignore])

#     self.object_ids = make_set(item_label, ignore=['none'])
#     self.categories = make_set(category_label, ignore=['none'])
#     self.exposures  = make_set(exposure_label)

#     self.label = label









# # save properties
# self.nframes   = self.imgs.shape[0]
# self.nfeatures = self.imgs.shape[1]







# # create a subgroup bold directory.
# run = func.create_group("run")

# self.masker = NiftiMasker(
#     standardize=True,
#     detrend=True,
#     memory="nilearn_cache",
#     memory_level=5)
# self.masker.fit()

# if run_prefix is not None:
#     self.find_runs(run_prefix)
#     self.load_runs()







