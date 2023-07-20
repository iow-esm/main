#!/bin/bash

if [ ! $# -eq 2 ]; then
	echo "Usage: `basename "$0"` <target-key> <setup-key>"
	exit
else
	target=$1
	setup=$2
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
	
setup_origin="`awk -v setup="$setup" '{if($1==setup){print $2}}' ${setups_file_name}`"

if [ -z "${setup_origin}" ]; then
	echo "Unknown setup. Please use a setup from the ${setups_file_name}."
	exit
elif [ "${setup_origin}" == "#" ]; then
	echo "Unknown setup. Please use a setup from the ${setups_file_name}."
	exit
else
	echo "Setup: ${setup_origin}"
fi

source ${local}/local_scripts/identify_target.sh $target

colon=`echo "${setup_origin}" | grep ":"`

echo ssh -t "${user_at_dest}" \"mkdir -p ${dest_folder}\"
ssh -t "${user_at_dest}" "mkdir -p ${dest_folder}"

last_deploy_name="./LAST_DEPLOYED_SETUPS_${target_keyword}"

if [ -z "$colon" ]; then
	echo "Update from local setup "`whoami`@`hostname`":${setup_origin} to ${dest} at " `date +%Y-%m-%d_%H-%M-%S` >> ${last_deploy_name}
	echo rsync -r -i -u ${setup_origin}/ ${dest}/.
	rsync -r -i -u ${setup_origin}/ ${dest}/.

elif [ "${setup_origin::8}" == "https://" ] && [ "${setup_origin:0-6}" == "tar.gz" ]; then

	echo "Download setup from ${setup_origin}."
	file_name="${setup_origin##*/}"
	echo ssh -t "${user_at_dest}" \"curl ${setup_origin} --output ${dest_folder}/$file_name\"
	echo "Be patient! This might take a little time..."
	ssh -t "${user_at_dest}" "curl ${setup_origin} --output ${dest_folder}/$file_name"

	folder_name=${file_name::-7}
	echo "Unpack setup in ${dest}."
	echo ssh -t "${user_at_dest}" \"cd ${dest_folder}; tar -xvf ${file_name} \&\& rm ${file_name}\"
	ssh -t "${user_at_dest}" "cd ${dest_folder}; tar -xvf ${file_name} && rm ${file_name}"

	echo ssh -t "${user_at_dest}" \"rsync -avz ${dest_folder}/${folder_name}/* ${dest_folder}/ \&\& rm -r ${dest_folder}/${folder_name}\"
	ssh -t "${user_at_dest}" "rsync -avz ${dest_folder}/${folder_name}/* ${dest_folder}/ && rm -r ${dest_folder}/${folder_name}"

	echo "Update from external setup ${setup_origin} to ${dest} at " `date +%Y-%m-%d_%H-%M-%S` >> ${last_deploy_name}

else
	# everything before the colon: user@target
	user_at_setup_origin="${setup_origin%:*}"

	# everything after the colon: /path/to/IOW_ESM
	setup_origin_folder="${setup_origin#*:}"
	
	if [ "${user_at_setup_origin}" != "${user_at_dest}" ]; then
		# if setup is located on different machine we have to copy the files (by resolving the symbolic links and preserving timestamps)
		echo ssh -t "${user_at_setup_origin}" \"rsync -r -i -u -t -L ${setup_origin_folder}/ ${dest}/.\"
		ssh -t "${user_at_setup_origin}" "rsync -r -i -u -t -L ${setup_origin_folder}/ ${dest}/."
		
	else
		# if setup is located on the machine we can leave symbolic links as is
		#echo ssh -t "${user_at_setup_origin}" \"cp -r ${setup_origin_folder}/* ${dest_folder}/.\"
		#ssh -t "${user_at_setup_origin}" "cp -r ${setup_origin_folder}/* ${dest_folder}/."
		echo ssh -t "${user_at_setup_origin}" \"rsync -r -i -u -t -l ${setup_origin_folder}/* ${dest_folder}/.\"
		ssh -t "${user_at_setup_origin}" "rsync -r -i -u -t -l ${setup_origin_folder}/* ${dest_folder}/."
	fi
	
	# some preparation scripts require write premissions
	echo ssh -t "${user_at_dest}" \"chmod u+w -R ${dest_folder}\"
	ssh -t "${user_at_dest}" "chmod u+w -R ${dest_folder}"

	ssh -t "${user_at_dest}" "cd ${dest_folder}; find . -type f -exec touch {} +"
	
	echo "Update from setup ${setup_origin} to ${dest} at " `date +%Y-%m-%d_%H-%M-%S` >> ${last_deploy_name}
fi

echo scp "${last_deploy_name}" ${user_at_dest}:${dest_folder}/LAST_DEPLOYED_SETUPS
scp "${last_deploy_name}" ${user_at_dest}:${dest_folder}/LAST_DEPLOYED_SETUPS