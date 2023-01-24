# This script will use the jobscript template defined in input/global_settings.py
# It will fill in _THREADS_, _NODES_, _CORES_ and _CORESPERNODE_ from the parallelization layout and save the jobscript as scripts/run/jobscript

import os
import shutil
import sys

try:
    input_name = str(sys.argv[1])
except:
    input_name = ""

# get current folder and check if it is scripts/run
mydir = os.getcwd()
if (mydir[-16:] != '/scripts/prepare'):
    print('usage: python3 ./create_jobscript.py')
    print('should be called from ${IOW_ESM_ROOT}/scripts/prepare')
    sys.exit()

# if we started from scripts/run we know our root directory
IOW_ESM_ROOT = mydir[0:-16]

# read global settings
sys.path.append(IOW_ESM_ROOT + "/scripts/run")
from parse_global_settings import GlobalSettings
global_settings = GlobalSettings(IOW_ESM_ROOT, input_name)

# call get_parallelization_layout
from get_parallelization_layout import get_parallelization_layout
parallelization_layout = get_parallelization_layout(global_settings)

# copy template file
file_name = IOW_ESM_ROOT+'/scripts/run/jobscript_' + input_name
if os.path.islink(file_name):
    os.system("cp --remove-destination `realpath " + file_name + "` " + file_name)

if global_settings.jobscript_template[0] != "/":   
    # copy relative to input directory 
    shutil.copyfile(global_settings.input_dir + "/" + global_settings.jobscript_template, file_name)
else:
    # copy from absolute path
    shutil.copyfile(global_settings.jobscript_template, file_name)

# replace the wildcards
#read input file
fin = open(file_name, 'rt')
#read file contents to string
data = fin.read()
#replace all occurrences of the required string
data = data.replace('_CORES_', str(parallelization_layout['total_cores']))
data = data.replace('_NODES_', str(parallelization_layout['total_nodes']))
data = data.replace('_CORESPERNODE_', str(global_settings.cores_per_node))

# add run name
data = data.replace('run.py', 'run.py '+input_name)

#close the input file
fin.close()
#open the input file in write mode
fin = open(file_name, 'wt')
#overrite the input file with the resulting data
fin.write(data)
#close the file
fin.close()

