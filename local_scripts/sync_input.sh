dest=$1

echo rsync -avz -u ./input/ $dest/input
rsync -avz -u ./input/ $dest/input
