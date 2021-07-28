if [ ! $# -eq 3 ]; then
	echo "Usage: `basename "$0"` <target-key> <base-setup-key> <archive-setup-key>"
	exit
else
	target=$1			# target means here the machine where this setup is located and has been successfully used
	base_setup=$2		# basic setup which has been initially used
	archive_setup=$3	# location where the archive will be created, 
						# files that are identical to the ones in the base setup will be just symbolic links
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
	echo "Unknown setup. Please use a setup from the ${setups_file_name}."
	exit
else
	echo "Setup archive: ${archive_setup_dest}"
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

# get all information of the target (machine where the setup is on at the moment)
source ${local}/local_scripts/identify_target.sh $target

# location of setup to archive
setup_location="${dest}"

# make a new directory for the setup
echo ssh -t "${user_at_base_setup_origin}" \"mkdir -p ${archive_dir}\"
ssh -t "${user_at_base_setup_origin}" "mkdir -p ${archive_dir}"

# create symbolic links to the base setup from which we will inherit
echo ssh -t "${user_at_base_setup_origin}" \"cp -as ${base_dir}/* ${archive_dir}/\"
ssh -t "${user_at_base_setup_origin}" "cp -as ${base_dir}/* ${archive_dir}/"

# make created links modifiable
echo ssh -t "${user_at_base_setup_origin}" \"chmod -R u+w ${archive_dir}\"
ssh -t "${user_at_base_setup_origin}" "chmod -R u+w ${archive_dir}"

# find out which files on the target are different (heuristic: they have different size) from the base setup
echo ssh -t "${user_at_base_setup_origin}" \""rsync -n -r -v --size-only ${setup_location}/input/ ${base_dir}/input/ | head -n -3 | tail -n +2 > include.txt"\"
ssh -t "${user_at_base_setup_origin}" "rsync -n -r -v --size-only ${setup_location}/input/ ${base_dir}/input/ | head -n -3 | tail -n +2 > include.txt"

# copy only these different files and replace the symbolic links
echo ssh -t "${user_at_base_setup_origin}" \"rsync -avz --files-from=include.txt ${setup_location}/input/ ${archive_dir}/input/\"
ssh -t "${user_at_base_setup_origin}" "rsync -avz --files-from=include.txt ${setup_location}/input/ ${archive_dir}/input/"

# modify the setup info and give information on the archive
echo ssh -t "${user_at_base_setup_origin}" \""cd ${archive_dir}; cp --remove-destination \$(readlink SETUP_INFO) SETUP_INFO; chmod u+w SETUP_INFO"\"
ssh -t "${user_at_base_setup_origin}" "cd ${archive_dir}; cp --remove-destination \$(readlink SETUP_INFO) SETUP_INFO; chmod u+w SETUP_INFO"

echo ssh -t "${user_at_base_setup_origin}" \""echo \"\" >> ${archive_dir}/SETUP_INFO; echo \"Setup archived from ${setup_location}/input/ at `date +%Y-%m-%d_%H-%M-%S`, differs from base setup ${base_dir}/input/ in files:\" >> ${archive_dir}/SETUP_INFO"\"
ssh -t "${user_at_base_setup_origin}" "echo \"\" >> ${archive_dir}/SETUP_INFO; echo \"Setup archived from ${setup_location}/input/ at `date +%Y-%m-%d_%H-%M-%S`, differs from base setup from ${base_dir}/input/ in files:\" >> ${archive_dir}/SETUP_INFO"

echo ssh -t "${user_at_base_setup_origin}" \""cat include.txt >> ${archive_dir}/SETUP_INFO; rm include.txt"\"
ssh -t "${user_at_base_setup_origin}" "cat include.txt >> ${archive_dir}/SETUP_INFO; rm include.txt"

# since we are archiving the files should be write-protected
echo ssh -t "${user_at_base_setup_origin}" \"chmod -R a-w ${archive_dir}\"
ssh -t "${user_at_base_setup_origin}" "chmod -R a-w ${archive_dir}"

