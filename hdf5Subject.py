#!/usr/bin/env python

# python specific modules
import os
from glob import glob
import logging
import numpy as np

# project specific modules
import h5py
import nibabel as nb
from config import config # study specific information - common across subjects

## Logging: good for debuging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(config.DATADIR,config.STUDY,'subject.log')

# specifies different handlers to be applied to logging file
formatter = logging.Formatter('%(levelname)s - %(name)s - %(funcName)s - %(message)s')

# set a handler to customize logging output
file_handler = logging.FileHandler(log_file, 'w')
file_handler.setFormatter(formatter)

# setting what get sent to log file and screen.
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# add the handler to this instance of the logger.
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
## Logging: good for debuging.


## Subject object to do the work.
# a class object to read in a subjects brain data and metadata into hdf5 format.
class Subject(object):
    def __init__(self, study_dir, subject, anat_dir=config.ANATDIR, func_dir=config.FUNCDIR, 
        run_prefix=None, func_file=config.FUNCFILE_P, meta_dir=config.METADIR, meta_files=None, verbose=False):

        # initialize directory varibles for the data we would like to grab. 
        self.study_dir   = study_dir
        self.subject_dir = os.path.join( study_dir, subject )
        self.group_check(self.subject_dir)
        self.anat_dir    = os.path.join( self.subject_dir, func_dir )
        self.func_dir    = os.path.join( self.subject_dir, func_dir )
        self.meta_dir    = os.path.join( self.subject_dir, meta_dir )
        logger.info('Working on Study: %s, Subject: %s' % (study_dir, subject))

        # check to make sure specified directories exist - also need to check for read access.
        self.group_check(self.anat_dir)
        self.group_check(self.func_dir)
        self.group_check(self.meta_dir)

        # specify files, metafiles, any directory descriptors.
        self.run_prefix  = run_prefix
        self.func_file   = func_file
        self.meta_files  = meta_files

        # create a subject .hdf5 to insert things into.
        self.hdf = h5py.File('%s.hdf5'%self.subject_dir,'w')

        self.find_funcs()
        self.load_funcs()
        self.runs_full_TR_index()

    # find runs based on some user input.
    def find_funcs(self, nb_load=True):
        logger.info('Finding functional runs.')
        logger.info('Loading as nifti objects? %s' % nb_load ) 
        
        # the run prefix we are trying to find in directory structure.
        match_this = os.path.join(self.func_dir, self.run_prefix+'*' )
        run_dirs   = [ d for d in glob(match_this) if os.path.isdir(d) ]
        
        # sorted lists have a subtly different way of ordering strings. 
        ordering   = sorted( [ int(os.path.basename(r).split('_')[-1]) for r in run_dirs ] )
        sorted_run_dirs = [ os.path.join(self.func_dir, self.run_prefix+str(i)) for i in ordering ]
        
        # query that the run directories found is the same as user specified (if user specified).
        test = (len(run_dirs) == config.RUNNUM)
        logger.debug('User-specified run number and found run number is equal? %s' % test)

        # print output if conditions for run directories is met.
        logger.info('Found: %s' % run_dirs )
        
        # load all runs
        runs = []
        for run in sorted_run_dirs:
            # this checks to make sure the image in the run exists. 
            fname = self.file_check(run, self.func_file)
            logger.info('Including vol, in order: %s' % fname)

            # load nifti... or not
            if nb_load:
                img = nb.load(fname)
                runs.append(img)
            else:
                runs.append(fname)

        # save data about the runs and the number of runs.
        self.runs   = runs
        self.n_runs = len(runs)

    # load in runs, gathering information about the data.
    def load_funcs(self):
        """ Loads nifti object data into hdf5, including some metadata """
        logger.info("Loading volumes")

        # creates an hdf5 group for functional directory
        self.func = self.hdf.create_group('func')
        self.hdf['func'].attrs['n_runs'] = self.n_runs

        # load in the runs into hdf5 format and add some metadata about the runs. 
        for i,r in enumerate( self.runs ):
            # put nifti object into HDF5 across all runs.
            dat = r.get_data()     # numpy 30d array of the data
            hdr = r.get_header()   # header information about the data
            aff = r.get_affine()   # get affine transformation

            # save it in hdf5
            #import pdb; pdb.set_trace()
            run_name = 'run_%02d'%(int(i)+1)
            self.hdf['func'].create_group( run_name )                     # creates a group (folder) for each run
            self.hdf['func'][run_name].create_dataset( 'data', data=dat)  # saves data to that folder 
            
            # cycle through each of the items in the header and transfer over to HDF5
            for k,v in hdr.items():
                self.hdf['func'][run_name].attrs['nifti1_' + k] = v
            
            # collect attributes or meta data about the data. 
            self.hdf['func'][run_name].attrs['nifti1_affine'] = aff
            self.hdf['func'][run_name].attrs['trs']   = dat.shape[-1]
            self.hdf['func'][run_name].attrs['run']   = i+1
            self.hdf['func'][run_name].attrs['r_ind'] = np.arange(0,dat.shape[-1])

    def runs_full_TR_index(self):
        """ Creates a full scan index as many of the files coming in have these attributes"""
        try:
            # counts the TRs across all runs.
            count_trs = 0
            # cycle through each run
            for i,r in self.hdf['func'].iteritems():
                if 'r_ind' not in self.hdf['func'][i].attrs:
                    logger.exception('Run specific index not found for %s' % i)
                # resets the tr counting vector
                tr_vector = []

                # cycles through the 'r_ind' attribute.
                for j in self.hdf['func'][i].attrs['r_ind']:
                    tr_vector.append( count_trs )
                    count_trs+=1

                # save to hdf functional run directory
                self.hdf['func'][i].attrs['f_ind'] = np.array( tr_vector )

            # check to make sure 'f_ind' attribute was created.
            f_ind_attribute = [ 'f_ind' in self.hdf['func'][i].attrs for i,r in self.hdf['func'].iteritems() ]

            # sets and n_TRs variable for the subject.
            self.n_TRs = ( tr_vector[-1]+1 )

        # check to make sure number of 'f_ind attributes = the number funcitonal runs'
        except sum(f_ind_attribute) != self.n_runs:
            logger.exception("Run specific indexes not being specified.")


    def combine_funcs(self, to_2d=True):
        """ This function combines data across runs."""

        # initialize empty array to become the container for all runs combined.
        arr = []

        # get the total number of runs. 
        all_trs = sum( [ self.hdf['func'][i].attrs['trs'] for i,r in self.hdf['func'].iteritems() ] )
        
        # concatenate runs 
        for i,r in self.hdr['func'].iteritems():
            data = self.hdf['func'][i]['data'][:]
            if to_rd:
                n_voxels = np.prod(data.shape[:-1])
                data     = data.reshape( n_voxels, data.shape[-1])
            # add run data to a list
            arr.append( data )

        # concatenate into a numpy array
        self.all_runs = np.concatenate( arr )

    # find the anatomy and corresponding files needed to register the anatomy to the functional based on some user input. 
    def find_anatomy(self, nb_load=True):
        pass
        # this needs some work.
        try:
            logger.info("Finding anatomy files.")
            fnames = [ self.file_check(self.anat_dir, config.T1w), 
                    self.file_check(self.anat_dir, config.T2w), 
                    self.file_check(self.anat_dir, config.FIELDMAPS) ]
            logger.info('Anatomy files found: %s' % fnames)

        except fnames == None:
        self.anat  = self.hdf.create_group("anatomy")

        if config.T1w is not None:
            fname = self.file_check( self.anat_dir, config.T1w)
            if self.verbose: print "found: ", fname
            self.T1w = self.anat.create_dataset("t1w")

    def load_anatomy(self, fname, nb_load=True):
        pass

    def find_metadata():
        pass

    def load_metadata():
        pass

    def group_check(self, group):
        if not os.path.exists(group):
            logger.critical('Cannot find directory: %s, make sure full path is specified' % fname)
        return group

    def file_check(self, group, file):
        fname = os.path.join( group, file )
        if not os.path.exists(fname):
            logger.critical('Cannot find file or volume: %s' % fname)
        return fname

## Subject object to do the work.





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







