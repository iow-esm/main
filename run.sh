#!/bin/bash

if [ $# -eq 0 ]; then
	echo "Usage: `basename "$0"` <target-key> [<update_from_local_setup>]"
	echo "<target-key> is one key that is contained in your ./DESTINATIONS file."
	echo "<update_from_local_setup> (optional) is by default false."
	echo "If set to true, you need to have in your ./SETUPS file a setup key \"local\"."
	echo "This key references a local setup source where you can make modifications during development."
	echo "The setup which is already located at the remote server is updated accordingly."
	exit
else
	target=$1
fi	


echo "###############################################"
echo "##                                           ##"
echo "##          IOW earth-system model           ##"
echo "##                                           ##"
echo "###############################################"
echo ""
echo "###############################################"
echo "##            Running the model              ##"
echo "###############################################"
echo ""


#available_args=("target" "update_from_local_setup")
#source ./local_scripts/parse_args.sh "${available_args[@]}" "," "$@"

echo "##       Identify the target of the run      ##"
echo "###############################################"
source ./local_scripts/identify_target.sh $target
echo ""
echo ""

# check if there are more optional arguments and process them
args=("$@")

# first optional argument: should we run prepare scripts before we run?
prepare_arg=1

echo "##     Check if model sould be prepared      ##"
echo "###############################################"
if [ "${args[${prepare_arg}]}" == 'prepare-before-run' ]; then
	inputs_arg=2				#if yes, possible setup-update arguments will follow at index 2
	prepare_before_run=true
	echo "The model will be prepared before the run."
else
	inputs_arg=1				#if no, possible setup-update arguments will follow at index 1
	prepare_before_run=false
	echo "The model will not be prepared before the run."
fi
echo ""
echo ""

echo "## Check if model output sould be synchronized to another target  ##"
echo "####################################################################"
next_arg="${args[${inputs_arg}]}"
next_arg="$(echo -e ${next_arg} | tr -d '[:space:]')" # trim away any white spaces
if [ "${next_arg:0:8}" == 'sync_to=' ]; then
	let inputs_arg=inputs_arg+1				#if yes, possible setup-update arguments will follow at index 2
	sync_to="${next_arg:8}"
	echo "The model output will be synchronized to ${sync_to}"
else
	sync_to=""
	echo "The model output will not be synchronized."
fi
echo ""
echo ""

echo "##  Check if various input folders are used  ##"
echo "###############################################"
for ((i = ${inputs_arg}; i < $#; i++)); do 
	echo "The input folder ${args[i]} will be used."
done
echo ""
echo ""


echo "##        Sync scripts to the target         ##"
echo "###############################################"
./local_scripts/sync_scripts.sh ${user_at_dest} ${dest_folder}
echo ""
echo ""

if [ -d ./postprocess ]; then
	echo "## Sync postprocessing scripts to the target ##"
	echo "###############################################"
	./local_scripts/sync_postprocess.sh ${target} ${user_at_dest} ${dest_folder}
	./local_scripts/tag_build.sh ${target_keyword} ${debug} "" "postprocess"
	echo ""
	echo ""
fi

echo "##        Gather info on last build          ##"
echo "###############################################"
./local_scripts/tag_build.sh ${target_keyword} ${debug} "" "main"
# this is name of the file where the tags are stored
last_build_file="LAST_BUILD_${target_keyword}_${debug}"
cat "${last_build_file}"
echo ""
echo "Transfer it to the target:"
echo scp "${last_build_file}" ${user_at_dest}:${dest_folder}/
scp "${last_build_file}" ${user_at_dest}:${dest_folder}/
echo ""
echo ""

if [ "${sync_to}" != "" ]; then
	echo "##      Start synchronization of output      ##"
	echo "###############################################"
	./sync.sh "${target_keyword}" "${sync_to}"
	echo ""
	echo ""
fi

if [ $inputs_arg -lt $# ]; then
	for ((i = ${inputs_arg}; i < $#; i++)); do 
		echo "##         Start the run on target           ##"
		echo "###############################################"
		echo "Start run with input folder ${args[i]}"
		./local_scripts/run_${target}.sh ${user_at_dest} ${dest_folder} ${prepare_before_run} "${args[i]}"
		echo ""
		echo ""
	done
else
	echo "##         Start the run on target           ##"
	echo "###############################################"
	echo "Start run with input folder"
	./local_scripts/run_${target}.sh ${user_at_dest} ${dest_folder} ${prepare_before_run}
	echo ""
	echo ""
fi

echo ""
echo "###############################################"
echo "##              Model is running             ##"
echo "###############################################"
echo ""