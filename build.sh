target=$1
debug=${2:-"release"}
fast=${3:-"fast"}

components=(
	"OASIS3-MCT"
	"flux_calculator"
	"CCLM"
	"MOM5"
)
	
for c in "${components[@]}"; do
	if [ -d components/"$c" ]; then
		cd components/"$c"
		./build.sh "$target" "$debug" "$fast"
		cd -
	else
		echo "Skipping not existing directory components/$c."
		echo "$c will not be built."
	fi
done