if [ $# -eq 0 ]; then
	echo "Usage: `basename "$0"` <target-key>"
	exit
else
	target=$1
fi	

source ./local_scripts/identify_target.sh $target

./local_scripts/sync_input.sh ${dest}

./local_scripts/sync_scripts.sh ${dest}

./local_scripts/tag_build.sh ${target} "" ""
echo scp "LAST_BUILD_$target" ${user_at_dest}:${dest_folder}/
scp "LAST_BUILD_$target" ${user_at_dest}:${dest_folder}/

./local_scripts/run_${target}.sh ${user_at_dest} ${dest_folder}


