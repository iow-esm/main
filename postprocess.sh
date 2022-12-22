#!/bin/bash

if [ $# -lt 3 ]; then
	echo "Usage: `basename "$0"` <target-key> <model-task> <path-to-output> [<from-date>] [<to-date>]"
	exit
else
	target="$1"
	model_task="$2"
	path_to_output="$3"
	from_date=${4:--1}
	to_date=${5:--1}
fi	


echo "###############################################"
echo "##                                           ##"
echo "##          IOW earth-system model           ##"
echo "##                                           ##"
echo "###############################################"
echo ""
echo "###############################################"
echo "##          Postprocess the model            ##"
echo "###############################################"
echo ""

local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

task_dir="${local}/postprocess/${model_task}"

# check if file exists as it should
if [ ! -d "${task_dir}" ]; then
    echo "${task_dir} does not exist."
	exit
fi

echo "##       Identify the target of the run      ##"
echo "###############################################"
source ${local}/local_scripts/identify_target.sh $target
echo ""
echo ""

echo "##        Sync scripts to the target         ##"
echo "###############################################"
./local_scripts/sync_postprocess.sh ${target} ${user_at_dest} ${dest_folder}
echo ""
echo ""

echo "##        Gather info on last build          ##"
echo "###############################################"
cd postprocess
../local_scripts/tag_build.sh ${target_keyword} "release" "fast" "postprocess"
cd ..

# this is name of the file where the tags are stored
last_build_file="LAST_BUILD_${target_keyword}_${debug}"
cat "${last_build_file}"
echo ""
echo "Transfer it to the target:"
echo scp "${last_build_file}" ${user_at_dest}:${dest_folder}/
scp "${last_build_file}" ${user_at_dest}:${dest_folder}/
echo ""
echo ""

echo "##      Start postprocessing on target       ##"
echo "###############################################"
echo ssh "${user_at_dest}" \"echo Process started in background on \`hostname\`";" cd ${dest_folder}/postprocess/${model_task}/";" source ../../load_modules.sh";" nohup ./postprocess.sh ${dest_folder}/output/${path_to_output} ${from_date} ${to_date} \> nohup.out 2\>\&1 \& \"
ssh "${user_at_dest}" "echo Process started in background on \`hostname\`; cd ${dest_folder}/postprocess/${model_task}/; source ../../load_modules.sh; nohup ./postprocess.sh ${dest_folder}/output/${path_to_output} ${from_date} ${to_date} > nohup.out 2>&1 &"

echo ""
echo "###############################################"
echo "##         Postprocessing is running         ##"
echo "###############################################"
echo ""