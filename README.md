# HDFcompress

### What are we doing here?
- We are archiving study data into hdf5 format. In doing this, we are taking account of idiosyncracies and unique features of study directories and standardizing them into commone format in the HDF5 data type.
- HDF5 format will allow us to archive data with all kinds of metadata, e.g. figures, papers, etc.
- From this process we will also be able more easily run analyses with participants across different studies, because of the common format structure.
- File naming conventions have tried to follow as closely as possible to the [BIDS format](http://bids.neuroimaging.io/)

### How it works.

#### Putting data into HDF5 format.
- Each study will get a config_[study].py file. This file should be filled out to the best of the ability by the researcher or by anyone seeking to archive a particular study.
- This file focuses on anatomy files, functional brain imaging files, and metadata about the functional brain images. These fields will allow us reconstruct some forms of analysis across subjects and across studies. Therefore, at the current moment in time, not all data is being systematically brought into the hdf5 format structure.
- The program will process the study according to the config file argument inputs. Errors should point in the direction of what needs to be debugged. 

#### Getting subjects from HDF5 format.
