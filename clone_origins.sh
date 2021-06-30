#!/bin/bash

# find out location of this script
local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# intended path to ORIGINS file
origins_file_name="${local}/ORIGINS"

# check if file exists as it should
if [ ! -f "$origins_file_name" ]; then
    echo "${origins_file_name} does not exist. Please pull it from the remote repository."
	exit
fi

# name for temporary cloning script
temporary_name=clone_origins_tmp.sh

# go through ORIGINS file and create temporary script for cloning
awk -v local="$local" '{
	dir=$1
	remote=$2
	
	print "if [ -d "local"/"dir"/.git ]; then"
	print " echo \""dir" is already a git repository. Just pull from "remote"\""
	print "else"
	print " mkdir -p "local"/"dir
	print " git clone "remote" "local"/"dir
	print "fi"

}' ${origins_file_name} > ${temporary_name}

# execute temporary file
chmod u+x ${temporary_name}
./${temporary_name}

# remove temporary file
rm ${temporary_name}
	

