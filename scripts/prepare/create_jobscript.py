# This script will use the jobscript template defined in input/global_settings.py
# It will fill in _THREADS_, _NODES_, _CORES_ and _CORESPERNODE_ from the parallelization layout and save the jobscript as scripts/run/jobscript

import os
import shutil
import sys

# get current folder and check if it is scripts/run
mydir = os.getcwd()
if (mydir[-16:] != '/scripts/prepare'):
    print('usage: python3 ./create_jobscript.py')
    print('should be called from ${IOW_ESM_ROOT}/scripts/prepare')
    sys.exit()

# if we started from scripts/run we know our root directory
IOW_ESM_ROOT = mydir[0:-16]

# read global settings
exec(open(IOW_ESM_ROOT+'/input/global_settings.py').read(),globals())

# call get_parallelization_layout
from get_parallelization_layout import get_parallelization_layout
parallelization_layout = get_parallelization_layout(IOW_ESM_ROOT)

# copy template file
file_name = IOW_ESM_ROOT+'/scripts/run/jobscript'
if os.path.islink(file_name):
    os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)
shutil.copyfile(IOW_ESM_ROOT+'/'+jobscript_template, file_name)

# replace the wildcards
#read input file
fin = open(IOW_ESM_ROOT+'/scripts/run/jobscript', 'rt')
#read file contents to string
data = fin.read()
#replace all occurrences of the required string
data = data.replace('_CORES_', str(parallelization_layout['total_cores']))
data = data.replace('_NODES_', str(parallelization_layout['total_nodes']))
data = data.replace('_CORESPERNODE_', str(cores_per_node))
#close the input file
fin.close()
#open the input file in write mode
fin = open(IOW_ESM_ROOT+'/scripts/run/jobscript', 'wt')
#overrite the input file with the resulting data
fin.write(data)
#close the file
fin.close()

