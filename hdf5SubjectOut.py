#!/usr/bin/env python
import os, re, logging
from glob import glob
import numpy as np

# project specific modules
import h5py
import nibabel as nb
from config import config

def check_hdf5(group, file):
    fname = os.path.join( group, file )
    if not os.path.exists(fname):
        logger.critical('Cannot find file or volume: %s' % fname)
    return fname

study   = os.path.basename(config.STUDYDIR)
outhdf5      = '%s_%s'%(study, sid)
outfile = '%s.hdf5'%outhdf5


## Logging: good for debuging.
logger = logging.getLogger(__name__)
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

# do stuff
s = h5py.File("No_45.hdf5", "r")

# transform HDF5 to nifti
def create_nifti(self):
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


# transform HDF5 to txt files
def create_metadata(self, cond_type):
    """ The metadata file format is two columns [full scan index, value at index] """
    # checks file exists 
    file = self.file_check(self.meta_dir, cond_type)

    # separates file type and string name of file.
    fileparts = os.path.basename( file ).split('.')
    if len( fileparts ) != 2:
        logger.criticalcal("Error processing file: %s, too many . in filebase"%file)
    
    # take file parts for processing. 
    basefile, filetype = fileparts

    # IMPORTANT, transfering the meta file description
    logger.info("Matching '%s' to one of: %s meta types" %(basefile, self.meta_types))
    pattern = [ t for t in self.meta_types if re.search(t, basefile) is not None ]
    logger.info("Found %s to bring into HDF5."%basefile)

    # catch any potential errors. 
    if len(pattern)>1:
        logger.critical(
            'Multiple patterns matched for meta files.'\
            'Must change meta file names to match a type from list below.'\
            '%s' %self.meta_types)
    else:
        logger.debug("Matched %s with %s" % (pattern[0], basefile) )
        attr_name  = pattern[0]

    # now we can load in the file.
    if filetype == 'csv':
        info = np.recfromcsv( file, names=['index', attr_name], delimiter=',' )

    elif filetype == 'txt':
        info = np.recfromcsv( file, names=['index', attr_name], delimiter='\t' )

    else:
        logger.exception( "%s, not .txt or .csv, chill out, we're not there yet..."%filename)

    # check to make sure we don't have more than 2 columns in meta data file
    if len(info[0])>2:
        logger.exception('The metadata file format is [full scan index, value at index]')

    # checks that the length of the info file is the same length as the number of TRs. 
    if len( info ) != (self.n_TRs):
        logger.exception( "Length of %s, does not match total # of TRs." % filename )

    # cycle through each run
    for i,r in self.hdf['func'].iteritems():
        walker = []

        # make sure run index matches
        run = self.hdf['func'][i].attrs['run']

        # cycles through each TR
        for j in self.hdf['func'][i].attrs['f_ind']:
            # append to vector if run index matches global index
            if run == info[j][0]:
                walker.append( info[j][1] )
            else:
                logger.critical("Run index and meta file do not match! AHH")

        # write to hdf5
        logger.info("No obvious errors processing %s file into hdf5"%filename)
        self.hdf['func'][i].attrs[attr_name] = np.array( walker )

