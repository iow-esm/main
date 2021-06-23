if [ $# -eq 0 ]; then
	target="`awk '{print $2}' LAST_BUILD`"
	echo "Run on $target"
else
	target=$1
fi	

source ./local_scripts/identify_target.sh $target

./local_scripts/sync_scripts.sh ${dest}

./local_scripts/run_${target}.sh ${user_at_dest} ${dest_folder}
