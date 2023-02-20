user_at_dest=$1
dest_folder=$2
prepare_before_run=${3:-false}
setup=${4:-""}

python_module="anaconda3/2019.10"

if [ ${prepare_before_run} == true ]; then
	echo ssh -t $user_at_dest "module load ${python_module}; cd $dest_folder/scripts/prepare; python3 ./create_mappings.py ${setup}"
	ssh -t $user_at_dest "module load ${python_module}; cd $dest_folder/scripts/prepare; python3 ./create_mappings.py ${setup}"
fi

echo ssh -t $user_at_dest "module load ${python_module}; cd $dest_folder/scripts/prepare; python3 ./create_jobscript.py ${setup}"
ssh -t $user_at_dest "module load ${python_module}; cd $dest_folder/scripts/prepare; python3 ./create_jobscript.py ${setup}"

echo ssh -t $user_at_dest "cd $dest_folder/scripts/run; sbatch jobscript_${setup}"
ssh -t $user_at_dest "cd $dest_folder/scripts/run; sbatch jobscript_${setup}"
