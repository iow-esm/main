user_at_dest=$1
dest_folder=$2
dest="${user_at_dest}:${dest_folder}"

echo ssh -t $user_at_dest \"mkdir -p $dest_folder/scripts/prepare\"
echo ssh -t $user_at_dest \"mkdir -p $dest_folder/scripts/run\"
ssh -t $user_at_dest "mkdir -p $dest_folder/scripts/prepare"
ssh -t $user_at_dest "mkdir -p $dest_folder/scripts/run"

echo rsync -r -i -u ./scripts/prepare/ $dest/scripts/prepare
echo rsync -r -i -u ./scripts/run/ $dest/scripts/run
rsync -r -i -u ./scripts/prepare/ $dest/scripts/prepare
rsync -r -i -u ./scripts/run/ $dest/scripts/run
