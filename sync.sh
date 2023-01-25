#!/bin/bash

src=$1
dst=$2
timeout=${3:-5}

source ./local_scripts/identify_target.sh $src

user_at_src=${user_at_dest} 
src_folder=${dest_folder}
src=${dest}

source ./local_scripts/identify_target.sh $dst

user_at_dst=${user_at_dest} 
dst_folder=${dest_folder}
dst=${dest}

script="cd ${dest_folder}; counter=0; terminate=0; while [ 1 ]; do let counter=counter+1; nohup rsync -r -i -u -l ${src}/* ${dest_folder}/ > nohup_\\\${counter}.out 2>&1; if [ \\\`cat nohup_\\\${counter}.out | wc -l\\\` -eq 1 ]; then let terminate=terminate+1; fi; if [ \\\$terminate -gt ${timeout} ]; then break; fi; sleep 3600; done"

echo ssh -t ${user_at_dst} \"mkdir -p ${dst_folder}\"
echo ssh -t ${user_at_dst} \"screen -dSm \\\"rsync-$1-$2\\\" bash -c \\\"$script\\\"";" sleep 1\"

ssh -t ${user_at_dst} "mkdir -p ${dst_folder}"
ssh  ${user_at_dst} -t "screen -dSm \"rsync-$1-$2\" bash -c \"$script\"; sleep 1"