target=$1
debug=${2:-"release"}
fast=${3:-"fast"}

set -e

# location of this script
local="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

origins=(`awk '{print $1}' ${local}/ORIGINS`)

echo "###############################################"
echo "##                                           ##"
echo "##          IOW earth-system model           ##"
echo "##                                           ##"
echo "###############################################"
echo ""
echo "###############################################"
echo "##             Building origins              ##"
echo "###############################################"
echo ""
	
for c in "${origins[@]}"; do
	if [ -f "${local}/${c}/build.sh" ]; then
		echo "## Build: $c"
		echo "###############################################"
		echo ""
		cd "${local}/$c"
		./build.sh "$target" "$debug" "$fast"
		cd -
		echo ""
		echo ""
	fi
done

echo ""
echo "###############################################"
echo "##               Building done               ##"
echo "###############################################"
echo ""