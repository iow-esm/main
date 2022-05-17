#!/bin/bash

echo "###############################################"
echo "##                                           ##"
echo "##          IOW earth-system model           ##"
echo "##                                           ##"
echo "###############################################"
echo ""
echo "###############################################"
echo "##             Cloning components            ##"
echo "###############################################"
echo ""

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
awk -v local="$local" -v ori="$1" '{
	dir=$1
	if (ori != ""){
		if (dir != ori){
			next
		}
	}
	remote=$2
	version=$3
	
	if (version != ""){
		branch="--branch "version
	}
	else{
		branch=""
	}
	
	print "if [ -d "local"/"dir"/.git ]; then"
	print " cd "local"/"dir
	print " if ! git pull "remote" "version"; then"
	print "  rm -rf "local"/"dir
	print " fi"
	print " cd -"
	print "else"
	print " mkdir -p "local"/"dir
	print " if ! git clone "branch" "remote" "local"/"dir"; then"
	print "  rm -r "local"/"dir
	print " fi"
	print "fi"

}' ${origins_file_name} > ${temporary_name}

# execute temporary file
chmod u+x ${temporary_name}
./${temporary_name}

# remove temporary file
rm ${temporary_name}
	
echo ""
echo "###############################################"
echo "##               Cloning done                ##"
echo "###############################################"
echo ""

