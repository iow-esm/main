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

#available_args=("target" "update_from_local_setup")
#source ./local_scripts/parse_args.sh "${available_args[@]}" "," "$@"

source ./local_scripts/identify_target.sh $target

if [ $# -gt 1 ]; then
	args=("$@")
	for ((i=1;i<$#;i++)); do 
		./deploy_setups.sh "$target" "${args[i]}"
	done
fi

./local_scripts/sync_scripts.sh ${user_at_dest} ${dest_folder}

./local_scripts/tag_build.sh ${target} "" ""
echo scp "LAST_BUILD_$target" ${user_at_dest}:${dest_folder}/
scp "LAST_BUILD_$target" ${user_at_dest}:${dest_folder}/

./local_scripts/run_${target}.sh ${user_at_dest} ${dest_folder}


