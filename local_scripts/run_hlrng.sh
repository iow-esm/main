user_at_dest=$1
dest_folder=$2
prepare_before_run=${3:-false}

python_module="anaconda3/2019.03"

if [ ${prepare_before_run} == true ]; then
	echo ssh -t $user_at_dest "module load ${python_module}; cd $dest_folder/scripts/prepare; python3 ./create_mappings.py"
	ssh -t $user_at_dest "module load ${python_module}; cd $dest_folder/scripts/prepare; python3 ./create_mappings.py"
fi

echo ssh -t $user_at_dest "module load ${python_module}; cd $dest_folder/scripts/prepare; python3 ./create_jobscript.py"
ssh -t $user_at_dest "module load ${python_module}; cd $dest_folder/scripts/prepare; python3 ./create_jobscript.py"

echo ssh -t $user_at_dest "cd $dest_folder/scripts/run; source ~/.bash_profile; sbatch jobscript"
ssh -t $user_at_dest "cd $dest_folder/scripts/run; source ~/.bash_profile; sbatch jobscript"
