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
	update_from_local_setup=${2:-"false"}
fi	

#available_args=("target" "update_from_local_setup")
#source ./local_scripts/parse_args.sh "${available_args[@]}" "," "$@"

source ./local_scripts/identify_target.sh $target

if [[ "${update_from_local_setup}" == "true" ]]; then
	setups_file_name="./SETUPS"
	setup_origin="`awk -v setup="local" '{if($1==setup){print $2}}' ${setups_file_name}`"
	echo "Updated from local setup "`whoami`@`hostname`":${setup_origin} at "`date +%Y-%m-%d_%H-%M-%S` >> "${setup_origin}"/LOCAL_SETUP_INFO
	./deploy_setups.sh "$target" local
fi

# TODO: to be removed. This should be done with the deploy_setups.sh script
./local_scripts/sync_input.sh ${dest}

./local_scripts/sync_scripts.sh ${dest}

./local_scripts/tag_build.sh ${target} "" ""
echo scp "LAST_BUILD_$target" ${user_at_dest}:${dest_folder}/
scp "LAST_BUILD_$target" ${user_at_dest}:${dest_folder}/

./local_scripts/run_${target}.sh ${user_at_dest} ${dest_folder}


