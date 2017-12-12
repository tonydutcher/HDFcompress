## CONFIG FILE FOR A SPECIFIC STUDY THAT PUTS DATA INTO HDF5 FORMAT

# --- PERC ---- #
# - IMAGING DATA
# path to where data is held - top level directory
DATADIR    = '/work/04635/adutcher/lonestar/compress_hdf/perc'

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
FUNCFILE_B = 'bold_mcf_brain_mask.nii.gz'
FUNCFILE_R = 'bold.nii.gz'

# movement files
MOVFILE    = 'bold_mcf.nii.gz.par'

# - METADATA ABOUT IMAGING DATA


# - RESULTS


# path to paper to be stored in top level directory.
