target=$1
user_at_dest=$2
dest_folder=$3
dest="${user_at_dest}:${dest_folder}"

echo ssh -t $user_at_dest \"mkdir -p $dest_folder/postprocess\"
ssh -t $user_at_dest "mkdir -p $dest_folder/postprocess"

echo rsync -r -i -u ./postprocess/* $dest/postprocess/
rsync -r -i -u ./postprocess/* $dest/postprocess/

echo rsync -r -i -u ./postprocess/load_modules_${target}.sh $dest/postprocess/load_modules.sh
rsync -r -i -u ./postprocess/load_modules_${target}.sh $dest/postprocess/load_modules.sh
