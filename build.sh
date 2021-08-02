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
	cd components/"$c"
	./build.sh "$target" "$debug" "$fast"
	cd -
done