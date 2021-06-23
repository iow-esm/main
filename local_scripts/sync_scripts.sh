dest=$1

echo rsync -avz -u ./scripts/prepare/ $dest/scripts/prepare
echo rsync -avz -u ./scripts/run/ $dest/scripts/run
rsync -avz -u ./scripts/prepare/ $dest/scripts/prepare
rsync -avz -u ./scripts/run/ $dest/scripts/run
