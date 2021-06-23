#!/bin/bash

if [ $# -lt 1 ]; then
	echo "Put a target from ../DESTINATIONS as first argument"
	exit
fi

target=$1
debug=${2:-"release"} # debug/release
fast=${3:-"fast"}	# fast/rebuild

local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

dest="`awk -v dest="$target" '{if($1==dest){print $2}}' ${local}/../DESTINATIONS`"

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
