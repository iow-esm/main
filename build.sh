target=$1
debug=${2:-"release"}
fast=${3:-"fast"}

set -e

components=(
	"OASIS3-MCT"
	"flux_calculator"
	"CCLM"
	"MOM5"
)

echo "###############################################"
echo "##                                           ##"
echo "##          IOW earth-system model           ##"
echo "##                                           ##"
echo "###############################################"
echo ""
echo "###############################################"
echo "##            Building components            ##"
echo "###############################################"
echo ""
	
for c in "${components[@]}"; do
	if [ -d components/"$c" ]; then
		echo "## Component: $c"
		echo "###############################################"
		echo ""
		cd components/"$c"
		./build.sh "$target" "$debug" "$fast"
		cd -
		echo ""
		echo ""
	else
		echo "## Skipping components/$c."
		echo "## $c will not be built."
		echo "###############################################"
		echo ""
		echo ""
	fi
done

echo ""
echo "###############################################"
echo "##               Building tools              ##"
echo "###############################################"
echo ""

tools=(
	"I2LM"
)
	
for c in "${tools[@]}"; do
	if [ -d tools/"$c" ]; then
		echo "## Tools: $c"
		echo "###############################################"
		echo ""
		cd tools/"$c"
		./build.sh "$target" "$debug" "$fast"
		cd -
		echo ""
		echo ""
	else
		echo "## Skipping tools/$c."
		echo "## $c will not be built."
		echo "###############################################"
		echo ""
		echo ""
	fi
done

echo ""
echo "###############################################"
echo "##               Building done               ##"
echo "###############################################"
echo ""