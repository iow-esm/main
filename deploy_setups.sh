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
else
	echo "Setup: ${setup_origin}"
fi

source ${local}/local_scripts/identify_target.sh $target

colon=`echo "${setup_origin}" | grep ":"`

echo ssh -t "${user_at_dest}" \"mkdir -p ${dest_folder}\"
ssh -t "${user_at_dest}" "mkdir -p ${dest_folder}"
if [ -z "$colon" ]; then
	echo "Update from local setup "`whoami`@`hostname`":${setup_origin} at "`date +%Y-%m-%d_%H-%M-%S` >> "${setup_origin}"/LOCAL_SETUP_INFO
	echo rsync -r -i -u ${setup_origin}/ ${dest}/.
	rsync -r -i -u ${setup_origin}/ ${dest}/.
else
	# everything before the colon: user@target
	user_at_setup_origin="${setup_origin%:*}"

	# everything after the colon: /path/to/IOW_ESM
	setup_origin_folder="${setup_origin#*:}"
	
	echo ssh -t "${user_at_setup_origin}" \"rsync -r -i -u ${setup_origin_folder}/ ${dest}/.\"
	ssh -t "${user_at_setup_origin}" "rsync -r -i -u ${setup_origin_folder}/ ${dest}/."
fi

# some preparation scripts require write premissions
echo ssh -t "${user_at_dest}" \"chmod u+w -R ${dest_folder}\"
ssh -t "${user_at_dest}" "chmod u+w -R ${dest_folder}"