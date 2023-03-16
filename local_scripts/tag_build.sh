#!/bin/bash

if [ $# -lt 4 ]; then
	echo "Usage: `basename "$0"` <target-key> <release/debug> <fast/rebuild> <component>"
	exit
fi

target=$1
debug=$2 # debug/release
fast=$3	# fast/rebuild

# location of this script
local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# this is name of the file where the tags are stored
last_build_file="${local}/../LAST_BUILD_${target}_${debug}"

# find out if the working directory has uncommitted changes
dirt=`git status | grep "nothing to commit"`
# if yes, grep did not find the string and the variable is empty thus we tag this
if [ -z "${dirt}" ]; then
	dirt="+uncommited"
else
	dirt=""
fi

# component name is the string after the last / in the path
component=$4 #${PWD##*/}

# build up the tag that should be recorded 
tag="$component `git show | head -n 1 | awk '{print $2}'`$dirt $fast `date +%Y-%m-%d_%H-%M-%S`"

# is this component already tagged?
if [ -f ${last_build_file} ]; then
	last_tag=`grep "^${component}" "${last_build_file}"`
	chmod u+rw  "${last_build_file}"
fi

# if not, we add it  
if [ -z "${last_tag}" ]; then
	if [ -f ${last_build_file} ]; then
		chmod u+rw "${last_build_file}"
	fi
	echo $tag >> ${last_build_file}
else # if yes, we replace the old tag with the new one
	sed -i s/"${last_tag}"/"$tag"/g ${last_build_file}
fi

#exit

if [ "${dirt}" == "+uncommited" ]; then

	difference="######## uncommited changes in ${component}"$'\n'
	difference="${difference}"`git diff`
	difference="${difference}"$'\n'"######## uncommited changes in $component"
else
	difference=""
fi
	
awk -v difference="${difference}" -v marker="######## uncommited changes in ${component}" '
BEGIN{ replace = 0 }
{
	# normal lines
	if(($0 != marker) && (replace == 0))
	{
		print $0
	}
	
	# find beginning of block
	if(($0 == marker) && (replace == 0))
	{
		replace = 1
		next
	}
	
	# find end of block
	if(($0 == marker) && (replace == 1))
	{
		replace = 0
	}
} 
END{
	if(difference != "")
	{
		print difference
	}
}' ${last_build_file} > tmp.file

mv tmp.file ${last_build_file}
