## CONFIG FILE FOR A SPECIFIC STUDY THAT PUTS DATA INTO HDF5 FORMAT

# --- PERC ---- #
# - IMAGING DATA
# path to where data is held - top level directory
DATADIR    = '/work/04635/adutcher/lonestar/HDFcompress'
STUDY      = 'perc'

# path to top level anatomy directory from data dir variable
# for file names add the proper image type suffic i.e. '.nii' or '.nii.gz'
ANATDIR    = 'anatomy'
FIELDMAPS  = ''
T1w        = 'spgr.nii.gz'
T2w        = 'pt1inplane.nii.gz'

# path to the top level functional directory from data dir variable (often multipe run directories within this directory)
FUNCDIR    = 'BOLD'

# the functional prefix before most functional images
RUNPREFIX  = 'functional_'
RUNNUM     = 10

# the fully processed data _P, brain_mask, _B, and raw data _R
FUNCFILE_P = 'bold_mcf_brain.nii.gz'
FUNCFILE_R = 'bold.nii.gz'

# movement files
MOVFILE    = 'bold_mcf.nii.gz.par'

# - BEHAVIORAL METADATA ABOUT IMAGING DATA
# these files should be as long as all funational runs combined!
# if it is not, the files should be padded so that it is
# ---- the goal here, is that each volume in our data has as much meta data about that volume as possible!!!
METADIR    = 'behav/pymvpa'
REST       = 'rest_vols.txt'
LOCALIZER  = 'loc_stimtype_vols.txt'
TASK       = 'study_vols.txt'
TEST       = ''

# condition files, these get more specific about the data, need more time to process these. 
CONDITION  = ['study_trial_3-5_vols.txt', 'study_type_3-5_vols.txt']

# - RESULTS


# path to paper to be stored in top level directory.
