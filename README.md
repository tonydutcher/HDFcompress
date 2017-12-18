# HDFcompress

### What are we doing here?
- We are archiving study data into hdf5 format. In doing this, we are taking account of idiosyncracies and unique features of study directories and standardizing them into commone format in the HDF5 data type.
- HDF5 format will allow us to archive data with all kinds of metadata, e.g. figures, papers, etc.
- From this process we will also be able more easily run analyses with participants across different studies, because of the common format structure.
- File naming conventions have tried to follow as closely as possible to the [BIDS format](http://bids.neuroimaging.io/)

#### Current form of the project
- For now, the program functions on one subject at a time.
- Also, the program only takes in functional brain imaging files and metadata about the functional brain images. These are the two main aspects of results and statistical analysis for a given study.
- Eventually, we will build up to including all data for an entire study, this will be addressed in the future.

### How it works.

#### Putting data into HDF5 format
- Each study will get a config_[study].py file. This file should be filled out to the best of the ability by the researcher or by anyone seeking to convert a particular study. This file must be in the config_files folder before running anything.
- The program will process the study according to the config file argument inputs. Errors should point in the direction of what needs to be debugged. 
- The program is focused around a single subject. 
The main worker for the program is HDFcompress.py, an example input is below 
```
HDFcompress.py -config 'config_[study].py' -sid 'No_32' -type 'process'
```
This will work on the 'perc' study, for subject 'No_32', and '-type' tells the program to bring that subject into hdf5 format.
- Data in hdf5 format is no longer human viewer friendly. 
- To view the data, follow the steps below.

### Features of the code.
- The main function uses an argument parser to easily and meaningfully parse input arguments. 
- The code uses python's logging module, which allows us to specify multiple logging levels depending on user preference. Logs are automatically saved as output in a .log file 
- Internally, the code runs a number of verifications, to make sure data put into HDF5 format is consistent with it's original format and type.
- The code is modular and well commented. This makes what is happening transparent and hopefully easier for others to interpret and contribute their own code if desired. 

### Short walk through
#### Viewing data in HDF5 format in python
- To view data in HDF5 format, follow these steps.
1. Open an interactive session in python.
2. load h5py, a python wrapper for hdf5 formatted data.
```
import h5py
f = h5py.File('perc_No_45.hdf5', 'r')
```
3. HDF5 data is formated like a directory tree, with groups and members of groups. The tree supports python dictionary indexing.
```
f.keys()

f['func']
```
4. To view data for run 3 type.
```
f['func']['run_03']['data'][0]
```
5. The meta data about this data is stored in the form of attributes, to see atrribute options type.
```
f['func']['run_03'].attrs.keys()
```
6. To view the attributes, type...
```
f.func['run_03'].attrs['f_ind']
```

In this format, the data is already in an analyzeable format and it is easy to bring more subjects into this framework and analyze across subject with tools from other python modules.
