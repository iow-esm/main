#!/bin/bash

local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

awk -v local="$local" '{
	dir=$1
	remote=$2
	
	print "if [ -d "local"/../"dir"/.git ]; then"
	print " echo \""dir" is already a git repository. Just pull from "remote"\""
	print "else"
	print " mkdir -p "local"/../"dir
	print " git clone "remote" "local"/../"dir
	print "fi"

}' ${local}/../ORIGINS > create_origins_tmp.sh

chmod u+x create_origins_tmp.sh
./create_origins_tmp.sh

rm create_origins_tmp.sh
	

