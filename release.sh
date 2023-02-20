#!/bin/bash

#######################################
## Enter new version here            ##
#######################################

new_version="1.03.00"
commit_message="Release $new_version

This is a new version with new features and bug fixes, see Readme.
Caution this version is not compatible to version 1.00.00 of the 8nm MOM5_Baltic setups! 
"

#######################################

#######################################
## Enter versions of components here ##
#######################################

origins=(
"components/OASIS3-MCT      :   1.00.01"
"components/flux_calculator :   1.02.00"
"components/MOM5            :   1.01.00"
"components/CCLM            :   1.00.03"
"tools/I2LM                 :   1.00.01"
"postprocess                :   1.02.00"
)

#######################################





#######################################
## Leave untouched                   ##
#######################################

ref=`git rev-parse --verify $new_version 2>&1 | awk '{print $1}'`
if [ "$ref" != "fatal:" ]; then
    echo "Version $new_version already exits. Abort."
    exit  
fi    

for ori in "${origins[@]}"; do
    version=${ori##*:}
    origin=${ori%:*}
    repo=`awk -v origin=$origin '{if(origin==$1){print $2}}' ORIGINS`
    ref=`git ls-remote --heads $repo $version | awk '{print $2}'`
    
    if [ -z $ref ]; then
        echo "Version $version not found for $origin at $repo. Abort."
        exit
    fi
done

git checkout -b ${new_version}

for ori in "${origins[@]}"; do
    version=${ori##*:}
    origin=${ori%:*}
    repo=`awk -v origin=$origin '{if(origin==$1){print $2}}' ORIGINS`
    echo "$origin" "$repo" "$version" >> ORIGINS.tmp
done

mv ORIGINS.tmp ORIGINS

git commit -m "${commit_message}" ORIGINS

git switch -

#######################################
