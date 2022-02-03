#!/bin/bash
if [ $# -lt 1 ]; then
	echo "Put a target from ../DESTINATIONS as first argument"
	exit
fi

target_keyword=$1
debug=${2:-"release"} # debug/release
fast=${3:-"fast"}	# fast/rebuild

local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ ! -f "${local}/../AVAILABLE_TARGETS" ]; then
    echo "There is no AVAILABLE_TARGETS file. Please pull it from the remote repository."
    exit
fi

available_targets=(`awk '{if(NF != 1){next}; if(substr($1,1,1) == "#"){next}; print $1}' ${local}/../AVAILABLE_TARGETS`)

target=`printf '%s\n' "${available_targets[@]}" | grep -w "${target_keyword%%_*}"`
if [ -z ${target} ]; then
	echo "The target ${target_keyword%_*} is not supported"
	exit
fi

dest="`awk -v dest="$target_keyword" '{if($1==dest){print $2}}' ${local}/../DESTINATIONS`"

if [ -z $dest ]; then
	echo "Unknown destination"
	echo "Please create ../DESTINATIONS as follows"
	echo "<taget_key> user@target:/path/to/IOW_ESM"
	echo "e.g. haumea1 sk1480@haumea1:/data/sk1480/IOW_ESM"
	exit
else
	echo "Destination: $dest"
fi

# everything before the colon: user@target
user_at_dest="${dest%:*}"

# everything after the colon: /path/to/IOW_ESM
dest_folder="${dest#*:}"