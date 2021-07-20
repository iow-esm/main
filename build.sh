target=$1
debug=${2:-"release"}
fast=${3:-"fast"}

cd components/OASIS3-MCT
#./build.sh "$target" "$debug" "$fast"
cd -

cd components/flux_calculator
./build.sh "$target" "$debug" "$fast"
cd -

cd components/CCLM
./build.sh "$target" "$debug" "$fast"
cd -

cd components/MOM5
./build.sh "$target" "$debug" "$fast"
cd -