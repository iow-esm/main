user_at_dest=$1
dest_folder=$2

echo ssh -t $user_at_dest "cd $dest_folder/scripts/run; source ~/.bash_profile; sbatch jobscript"
ssh -t $user_at_dest "cd $dest_folder/scripts/run; source ~/.bash_profile; sbatch jobscript"
