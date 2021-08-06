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

# check if there are more optional arguments
if [ $# -gt 1 ]; then
	
	args=("$@")
	
	# first optional argument: should we run prepare scripts before we run?
	prepare_arg=1
	
	echo "##     Check if model sould be prepared      ##"
	echo "###############################################"
	if [ "${args[${prepare_arg}]}" == 'prepare-before-run' ]; then
		setups_arg=2				#if yes, possible setup-update arguments will follow at index 2
		prepare_before_run=true
		echo "The model will be prepared before the run."
	else
		setups_arg=1				#if no, possible setup-update arguments will follow at index 1
		prepare_before_run=false
		echo "The model will not be prepared before the run."
	fi
	echo ""
	echo ""
	
	echo "##   Check if the setup will be updated      ##"
	echo "###############################################"
	for ((i = ${setups_arg}; i < $#; i++)); do 
		echo "The setup will be updated."
		./deploy_setups.sh "$target" "${args[i]}"
	done
	echo ""
	echo ""
fi

echo "##        Sync scripts to the target         ##"
echo "###############################################"
./local_scripts/sync_scripts.sh ${user_at_dest} ${dest_folder}
echo ""
echo ""

echo "##        Gather info on last build          ##"
echo "###############################################"
./local_scripts/tag_build.sh ${target} ${debug} ""
# this is name of the file where the tags are stored
last_build_file="LAST_BUILD_${target}_${debug}"
cat "${last_build_file}"
echo ""
echo "Transfer it to the target:"
echo scp "${last_build_file}" ${user_at_dest}:${dest_folder}/
scp "${last_build_file}" ${user_at_dest}:${dest_folder}/
echo ""
echo ""

echo "##         Start the run on target           ##"
echo "###############################################"
./local_scripts/run_${target}.sh ${user_at_dest} ${dest_folder} ${prepare_before_run}
echo ""
echo ""

echo ""
echo "###############################################"
echo "##              Model is running             ##"
echo "###############################################"
echo ""