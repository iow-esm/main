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

local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

task_dir="${local}/postprocess/${model_task}"

# check if file exists as it should
if [ ! -d "${task_dir}" ]; then
    echo "${task_dir} does not exist."
	exit
fi

source ${local}/local_scripts/identify_target.sh $target

local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo ssh -t "${user_at_dest}" \"mkdir -p ${dest_folder}/postprocess/auxiliary\"
ssh -t "${user_at_dest}" "mkdir -p ${dest_folder}/postprocess/auxiliary"

echo rsync -r -i -u ${local}/postprocess/auxiliary/ ${dest}/postprocess/auxiliary/.
rsync -r -i -u ${local}/postprocess/auxiliary/ ${dest}/postprocess/auxiliary/.

echo ssh -t "${user_at_dest}" \"mkdir -p ${dest_folder}/postprocess/${model_task}\"
ssh -t "${user_at_dest}" "mkdir -p ${dest_folder}/postprocess/${model_task}"

echo rsync -r -i -u ${local}/postprocess/${model_task}/ ${dest}/postprocess/${model_task}/.
rsync -r -i -u ${local}/postprocess/${model_task}/ ${dest}/postprocess/${model_task}/.

echo rsync -r -i -u ${local}/postprocess/load_modules_${target}.sh ${dest}/postprocess/load_modules.sh
rsync -r -i -u ${local}/postprocess/load_modules_${target}.sh ${dest}/postprocess/load_modules.sh

echo ssh "${user_at_dest}" \"echo Process started in background on \`hostname\`";" cd ${dest_folder}/postprocess/${model_task}/";" source ../../load_modules_${target}.sh";" nohup ./postprocess.sh ${path_to_output} ${from_date} ${to_date} \> nohup.out 2\>\&1 \& \"
ssh "${user_at_dest}" "echo Process started in background on \`hostname\`; cd ${dest_folder}/postprocess/${model_task}/; source ../../load_modules_${target}.sh; nohup ./postprocess.sh ${path_to_output} ${from_date} ${to_date} > nohup.out 2>&1 &"