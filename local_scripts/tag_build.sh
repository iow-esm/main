#!/bin/bash

if [ $# -lt 3 ]; then
	echo "Usage: `basename "$0"` <target-key> <release/debug> <fast/rebuild>"
	exit
fi

target=$1
debug=$2 # debug/release
fast=$3	# fast/rebuild

# location of this script
local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# this is name of the file where the tags are stored
last_build_file="${local}/../LAST_BUILD_$target"

# find out if the working directory has uncommitted changes
dirt=`git status | grep "nothing to commit, working tree clean"`
# if yes, grep did not find the string and the variable is empty thus we tag this
if [ -z "${dirt}" ]; then
	dirt="+uncommited"
else
	dirt=""
fi

# component name is the string after the last / in the path
component=${PWD##*/}

# build up the tag that should be recorded 
tag="$component `git show | head -n 1 | awk '{print $2}'`$dirt $debug $fast `date +%Y-%m-%d_%H-%M-%S`"

# is this component already tagged?
last_tag=`grep "${component}" "${last_build_file}"`

# if not, we add it  
if [ -z "${last_tag}" ]; then
	echo $tag >> ${last_build_file}
else # if yes, we replace the old tag with the new one
	sed -i s."${last_tag}"."$tag".g ${last_build_file}
fi
