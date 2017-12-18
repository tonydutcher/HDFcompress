#!/usr/bin/env python
import os, re, logging
from glob import glob
import numpy as np

# project specific modules
import h5py
import nibabel as nb

## Logging: good for debuging.
logger = logging.getLogger(__name__)

## Subject object to do the work.
# a class object to read in a subjects brain data and metadata into hdf5 format.
class processSubject(object):
    def __init__(self, config, subject, log_level=10):
        self.config = config
        
        # makes sure the study and subject idrectories exist and sets up logging
        self.study_dir   = config.STUDYDIR
        self.subject_dir = os.path.join( self.study_dir, subject )
        self.group_check( self.subject_dir )
        study_name   = os.path.basename(self.study_dir)

        # check output directory
        self.out_dir     = config.OUTDIR
        self.group_check(self.out_dir)

        # logging stuff
        log_file   = os.path.join( self.out_dir, '%s_%s.log'%(study_name, subject) )
        logger.setLevel( log_level )

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

        # set-up the rest of the directories. 
        self.anat_dir    = os.path.join( self.subject_dir, config.ANATDIR )
        self.func_dir    = os.path.join( self.subject_dir, config.FUNCDIR )
        self.meta_dir    = os.path.join( self.subject_dir, config.METADIR )
        logger.info('Working on Study: %s, Subject: %s' % (self.study_dir, subject))

        # check to make sure specified directories exist - also need to check for read access.
        self.group_check(self.anat_dir)
        self.group_check(self.func_dir)
        self.group_check(self.meta_dir)

        # specify files, metafiles, any directory descriptors.
        self.run_prefix  = config.RUNPREFIX
        self.func_file   = config.FUNCFILE_P
        self.meta_types  = ['rest', 'loc', 'study', 'test']

        # create a subject .hdf5 to insert things into.
        outhdf5      = os.path.join(self.out_dir, '%s_%s'%(study_name, subject))
        self.outfile = '%s.hdf5'%outhdf5

        # create file if one does not already exist.
        if not os.path.exists(self.outfile):
            self.hdf = h5py.File(self.outfile,'w')
            logger.info("HDF5 file does not exist creating, %s"%self.outfile)
        else:
            self.hdf = h5py.File(self.outfile,'r+')
            logger.info("HDF5 file %s, already exists"%self.outfile)

        self.find_funcs()
        self.load_funcs()
        self.runs_full_TR_index()
        self.process_metadata(config.REST)
        self.process_metadata(config.LOCALIZER)
        self.process_metadata(config.TASK)

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
                walker = []

                # cycles through the 'r_ind' attribute.
                for j in self.hdf['func'][i].attrs['r_ind']:
                    walker.append( count_trs )
                    count_trs+=1

                # save to hdf functional run directory
                self.hdf['func'][i].attrs['f_ind'] = np.array( walker )

            # check to make sure 'f_ind' attribute was created.
            f_ind_attribute = [ 'f_ind' in self.hdf['func'][i].attrs for i,r in self.hdf['func'].iteritems() ]

            # sets and n_TRs variable for the subject.
            self.n_TRs = ( walker[-1]+1 )

        # check to make sure number of 'f_ind attributes = the number funcitonal runs'
        except:
            logger.exception("Run specific indexes not being specified.")


    def combine_funcs(self, to_2d=True):
        """ This function combines data across runs into a single data frame. 
            - the option to move this to """

        # initialize empty array to become the container for all runs combined.
        arr = []

        # get the total number of runs. 
        all_trs = sum( [ self.hdf['func'][i].attrs['trs'] for i,r in self.hdf['func'].iteritems() ] )
        
        # concatenate runs 
        for i,r in self.hdr['func'].iteritems():
            data = self.hdf['func'][i]['data'][:]
            if to_rd:
                n_voxels = np.prod(data.shape[:-1])
                data     = data.reshape(n_voxels, data.shape[-1])
            # add run data to a list
            arr.append( data )

        # concatenate into a numpy array
        self.all_runs = np.concatenate( arr )

    # # find the anatomy and corresponding files needed to register the anatomy to the functional based on some user input. 
    # def find_anatomy(self, nb_load=True):
    #     logger.info("Matching '%s' to one of: %s meta types" %(basefile, self.meta_types))
    #     pattern = [ t for t in self.meta_types if re.search(t, basefile) is not None ]
    #     # this needs some work.
    #     try:
    #         logger.info("Finding anatomy files.")
    #         fnames = [ self.file_check(self.anat_dir, config.T1w), 
    #                 self.file_check(self.anat_dir, config.T2w), 
    #                 self.file_check(self.anat_dir, config.FIELDMAPS) ]
    #         logger.info('Anatomy files found: %s' % fnames)

    #     except fnames == None:
    #     self.anat_dir  = self.hdf.create_group("anatomy")

    #     if config.T1w is not None:
    #         fname = self.file_check( self.anat_dir, config.T1w)
    #         if self.verbose: print "found: ", fname
    #         self.T1w = self.anat.create_dataset("t1w")

    def load_anatomy(self, fname, nb_load=True):
        pass

    def process_metadata(self, filename):
        """ The metadata file format is two columns [full scan index, value at index] """
        # checks file exists 
        file = self.file_check(self.meta_dir, filename)

        # separates file type and string name of file.
        fileparts = os.path.basename( file ).split('.')
        if len( fileparts ) != 2:
            logger.error("Error processing file: %s, too many . in filebase"%file)
        
        # take file parts for processing. 
        basefile, filetype = fileparts

        # IMPORTANT, transfering the meta file description
        logger.info("Matching '%s' to one of: %s meta types" %(basefile, self.meta_types))
        pattern = [ t for t in self.meta_types if re.search(t, basefile) is not None ]
        logger.info("Found %s to bring into HDF5."%basefile)

        # catch any potential errors. 
        if len(pattern)>1:
            logger.error(
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
            logger.exception( "Length of %s, does not match total # of TRs."%filename )

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
                    logger.error("Run index and meta file do not match! AHH")

            # write to hdf5
            logger.info("No obvious errors processing %s file into hdf5"%filename)
            self.hdf['func'][i].attrs[attr_name] = np.array( walker )
    

    # helper functions to make sure files exist
    def group_check(self, group):
        if not os.path.exists(group):
            logger.error('Cannot find directory: %s, make sure full path is specified'%group)
        return group

    # helper function to make 
    def file_check(self, group, file):
        fname = os.path.join( group, file )
        if not os.path.exists(fname):
            logger.error('Cannot find file or volume: %s'%fname)
        return fname
