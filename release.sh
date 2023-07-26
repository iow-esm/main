#!/bin/bash

#######################################
## Enter new version here            ##
#######################################

new_version="1.04.00"
commit_message="Release $new_version

This is a new version with new features and bug fixes, see Readme. 
"

#######################################

#######################################
## Enter versions of components here ##
#######################################

origins=(
"components/OASIS3-MCT      :   1.00.02"
"components/flux_calculator :   1.03.00"
"components/MOM5            :   1.01.01"
"components/CCLM            :   1.01.00"
"tools/I2LM                 :   1.00.02"
"postprocess                :   1.03.00"
"tester                     :   1.00.00"
"patch                      :   1.00.00"
)

#######################################





#######################################
## Leave untouched                   ##
#######################################

# create IOW version and public github version simultaneously
for v in "${new_version}" "github/${new_version}"; do

    # if we have a github version we need different origins file
    if [[ "${v}" =~ "github/" ]]; then
        sed s%git.io-warnemuende.de/iow_esm%github.com/iow-esm%g ORIGINS > ORIGINS.github
        origins_file="ORIGINS.github"
    else
        origins_file="ORIGINS"
    fi

    ref=`git rev-parse --verify $v 2>&1 | awk '{print $1}'`
    if [ "$ref" != "fatal:" ]; then
        echo "Version $v already exits. Abort."
        exit  
    fi    

    for ori in "${origins[@]}"; do
        version=${ori##*:}
        origin=${ori%:*}
        repo=`awk -v origin=$origin '{if(origin==$1){print $2}}' ${origins_file}`
        ref=`git ls-remote --heads $repo $version | awk '{print $2}'`

        if [ $? != 0 ]; then
            echo "Could not get info for $version of $origin at $repo. Abort."
            exit   
        fi     
        
        if [ -z "$ref" ]; then
            echo "Version $version not found for $origin at $repo. Abort."
            exit
        fi
    done

    git checkout -b ${v}

    for ori in "${origins[@]}"; do
        version=${ori##*:}
        origin=${ori%:*}
        repo=`awk -v origin=$origin '{if(origin==$1){print $2}}' ${origins_file}`
        echo "$origin" "$repo" "$version" >> ORIGINS.tmp
    done

    mv ORIGINS.tmp ORIGINS

    if [[ "${v}" =~ "github/" ]]; then
        rm "ORIGINS.github" 
    fi   

    git commit -m "${commit_message}" ORIGINS

    git switch -

done

#######################################
