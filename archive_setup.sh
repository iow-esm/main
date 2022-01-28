if [ ! $# -eq 3 ]; then
	echo "Usage: `basename "$0"` <target-key> <base-setup-key> <archive-setup-key>"
	exit
else
	target=$1			# target means here the machine where this setup is located and has been successfully used
	base_setup=$2		# basic setup which has been initially used
	archive_setup=$3	# location where the archive will be created, 
						# files that are identical to the ones in the base setup will be just symbolic links
	#remove_base=${4:-false}	# remove the base after archiving (only in preparation, very dangerous)
fi	

local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

setups_file_name="$local/SETUPS"

# check if file exists as it should
if [ ! -f "${setups_file_name}" ]; then
    echo "${setups_file_name} does not exist. Please create it as follows"
	echo "<setup_key> user@target:/path/to/IOW_ESM"
	echo "e.g. testing karsten@phy-2:/silod7/karsten/setups/IOW_ESM/testing"
	exit
fi

# from which base setup should this archive inherit	
base_setup_origin="`awk -v setup="${base_setup}" '{if($1==setup){print $2}}' ${setups_file_name}`"

if [ -z "${base_setup_origin}" ]; then
	echo "Unknown setup. Please use a setup from the ${setups_file_name}."
	exit
else
	echo "Base setup: ${base_setup_origin}"
fi

# where should the archive be stored
archive_setup_dest="`awk -v setup="${archive_setup}" '{if($1==setup){print $2}}' ${setups_file_name}`"

if [ -z "${archive_setup_dest}" ]; then
	echo "Setup not found in ${setups_file_name}."
	archive_setup_dest="${base_setup_origin}_${archive_setup}"
	echo "We will thus create it at ${archive_setup_dest}"
else
	echo "Use setup archive from ${setups_file_name}: ${archive_setup_dest}"
fi

# access remote machine with base setup: get user and hostname
user_at_base_setup_origin="${base_setup_origin%:*}"

# since we use soft links, base setup and archive destination must be on the same machine
if [ "${user_at_base_setup_origin}" != "${archive_setup_dest%:*}" ]; then
	echo "${user_at_base_setup_origin}" != "${archive_setup_dest%:*}"
	echo "Base setup and archive must be on the same machine"
	exit
fi

# everything after the colon: /path/to/setup
base_dir="${base_setup_origin#*:}"
archive_dir="${archive_setup_dest#*:}"

# if base and archive coincide: we want to create a base from our setup
if [ "${base_dir}" == "${archive_dir}" ]; then
	create_base=true
else	
	create_base=false
fi

# get all information of the target (machine where the setup is on at the moment)
source ${local}/local_scripts/identify_target.sh $target

# location of setup to archive
if [ "$user_at_dest" == "${user_at_base_setup_origin}" ]; then
	# everything is on the same machine, we can copy directly to the folder
	setup_location="${dest_folder}"
else
	# setup and archive are not on the same machine, we have to copy via ssh
	setup_location="${dest}"
fi

# make a new directory for the setup
echo ssh -t "${user_at_base_setup_origin}" \"mkdir -p ${archive_dir}/input\"
ssh -t "${user_at_base_setup_origin}" "mkdir -p ${archive_dir}/input"

if [ $create_base == false ]; then

	# create symbolic links to the base setup from which we will inherit
	echo ssh -t "${user_at_base_setup_origin}" \"cp -as ${base_dir}/* ${archive_dir}/\"
	ssh -t "${user_at_base_setup_origin}" "cp -as ${base_dir}/* ${archive_dir}/"

	# make created links modifiable
	echo ssh -t "${user_at_base_setup_origin}" \"chmod -R u+w ${archive_dir}\"
	ssh -t "${user_at_base_setup_origin}" "chmod -R u+w ${archive_dir}"
	
fi

# find out which files on the target are different from the base setup (important: base setup and setup on target should share the same timestamps)
echo ssh -t "${user_at_base_setup_origin}" \""rsync -n -r -v -L ${setup_location}/input/ ${base_dir}/input/ | head -n -3 | tail -n +2 > include.txt"\"
ssh -t "${user_at_base_setup_origin}" "rsync -n -r -v -L ${setup_location}/input/ ${base_dir}/input/ | head -n -3 | tail -n +2 > include.txt"

# copy only these different files and replace the symbolic links
echo ssh -t "${user_at_base_setup_origin}" \"rsync -avz --files-from=include.txt ${setup_location}/input/ ${archive_dir}/input/\"
ssh -t "${user_at_base_setup_origin}" "rsync -avz --files-from=include.txt ${setup_location}/input/ ${archive_dir}/input/"

if [ $create_base == false ]; then	

	# modify the setup info and give information on the archive
	echo ssh -t "${user_at_base_setup_origin}" \""cd ${archive_dir}; cp --remove-destination \$(readlink SETUP_INFO) SETUP_INFO; chmod u+w SETUP_INFO"\"
	ssh -t "${user_at_base_setup_origin}" "cd ${archive_dir}; cp --remove-destination \$(readlink SETUP_INFO) SETUP_INFO; chmod u+w SETUP_INFO"
	
	info="Setup archived from ${setup_location}/input/ at `date +%Y-%m-%d_%H-%M-%S`, differs from base setup ${base_dir}/input/ in files:"
	
	echo ssh -t "${user_at_base_setup_origin}" \""echo \"\" >> ${archive_dir}/SETUP_INFO; echo \"$info\" >> ${archive_dir}/SETUP_INFO"\"
	ssh -t "${user_at_base_setup_origin}" "echo \"\" >> ${archive_dir}/SETUP_INFO; echo \"$info\" >> ${archive_dir}/SETUP_INFO"
else

	info="Setup archived from ${setup_location}/input/ at `date +%Y-%m-%d_%H-%M-%S`."$'\n'
	info="$info""Setup correpsonds to global settings"$'\n'
	info="$info""####################################"$'\n'
	
	echo ssh -t "${user_at_base_setup_origin}" \""echo \"\" >> ${archive_dir}/SETUP_INFO; echo \"$info\" >> ${archive_dir}/SETUP_INFO"\"
	ssh -t "${user_at_base_setup_origin}" "echo \"\" >> ${archive_dir}/SETUP_INFO; echo \"$info\" >> ${archive_dir}/SETUP_INFO"

	echo ssh -t "${user_at_base_setup_origin}" "cat ${archive_dir}/input/global_settings.py >> ${archive_dir}/SETUP_INFO"
	ssh -t "${user_at_base_setup_origin}" "cat ${archive_dir}/input/global_settings.py >> ${archive_dir}/SETUP_INFO"

	info="####################################"$'\n'
	info="$info""archived files:"
	
	echo ssh -t "${user_at_base_setup_origin}" \""echo \"\" >> ${archive_dir}/SETUP_INFO; echo \"$info\" >> ${archive_dir}/SETUP_INFO"\"
	ssh -t "${user_at_base_setup_origin}" "echo \"\" >> ${archive_dir}/SETUP_INFO; echo \"$info\" >> ${archive_dir}/SETUP_INFO"

fi

echo ssh -t "${user_at_base_setup_origin}" \""cat include.txt >> ${archive_dir}/SETUP_INFO; rm include.txt"\"
ssh -t "${user_at_base_setup_origin}" "cat include.txt >> ${archive_dir}/SETUP_INFO; rm include.txt"

#if [ ! $create_base ]; then	
	#if [ ${remove_base} == true ]; then
	#	ssh -t "${user_at_base_setup_origin}" "chmod -R u+w ${archive_dir}"
	#	# find all remaining links and replace them by the originals
	#	ssh -t "${user_at_base_setup_origin}" "for f in `find ${archive_dir} ! -type d ! -type f`; do mv `readlink $f` $f; done"
	#	# remove the base setup
	#	ssh -t "${user_at_base_setup_origin}" "rm -rf ${archive_dir}"
	#fi
#fi

# update setup info at setup location
echo ssh -t "${user_at_base_setup_origin}" \"rsync -avz ${archive_dir}/SETUP_INFO ${setup_location}/\"
ssh -t "${user_at_base_setup_origin}" "rsync -avz ${archive_dir}/SETUP_INFO ${setup_location}/"

# since we are archiving the files should be write-protected
echo ssh -t "${user_at_base_setup_origin}" \"chmod -R a-w ${archive_dir}\"
ssh -t "${user_at_base_setup_origin}" "chmod -R a-w ${archive_dir}"