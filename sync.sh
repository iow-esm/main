#!/bin/bash

src=$1
dst=$2
timeout=${3:-5}

source ./local_scripts/identify_target.sh $src

user_at_src=${user_at_dest} 
src_folder=${dest_folder}
src=${dest}

source ./local_scripts/identify_target.sh $dst

user_at_dst=${user_at_dest} 
dst_folder=${dest_folder}
dst=${dest}

cat <<eof > local_sync_script.sh

my_PID=\$\$

function log(){
    echo \$1 >> sync_log.txt
}

# this function will run in the background and checks if synchronization is still needed
function check_for_running() {

    cd ${dest_folder}

    log "Check if any model is still running"
    while [ 1 ]; do
        # perform dry run (-n)
        started=\`ssh -t ${user_at_src} "ls ${src_folder}/*started.txt 2> /dev/null | wc -l"\`
        finished=\`ssh -t ${user_at_src} "ls ${src_folder}/*finished.txt 2> /dev/null | wc -l"\`
        failed=\`ssh -t ${user_at_src} "ls ${src_folder}/*failed.txt 2> /dev/null | wc -l"\`
        let running=started-finished-failed
        if [ \$running -eq 0 ]; then
            # if no model is running we stop
            log "No model running anymore"
            break
        fi
        sleep 10
    done

    log "Kill running snchronization to stop the hourly loop and remove PID file"
    while [ ! -f PID-$1-$2 ]; do
        sleep 5
    done
    pkill -P \`cat PID-$1-$2\`
    rm PID-$1-$2

    sleep 5

    log "Perform a last snychronization"
    ./rsync-$1-$2.sh last

    #wait

    log "Kill the synchronization as such. Goodbye."
    #pkill -P ${my_PID}
    screen_PID=\`ps ux | grep "SCREEN -dSm rsync-$1-$2" | grep -v "grep" | awk '{print \$2}'\`
    pkill -P \${screen_PID}
}

cd ${dest_folder}
rm sync_log.txt

log "Create script that performs the actual synchronization"
cat <<EOF > rsync-$1-$2.sh
echo \\\$BASHPID
counter=\\\$1 
rsync -r -i -u -l --exclude 'work' ${src}/* ${dest_folder}/ > sync_\\\${counter}.out 2>&1
EOF

log "Make file executable"
chmod u+x rsync-$1-$2.sh

log "Start checking if synchronization is still needed in background"
check_for_running &

# wait a little bit
#sleep 30

log "Start synchronization loop that is called every hour"
counter=0
while [ 1 ]; do 
    let counter=counter+1
    ./rsync-$1-$2.sh \$counter > PID-$1-$2

    sleep 5

    # if the output file does not exist anymore it means that check_for_running has killed the synchronization 
    # and we can stop here
    if [ ! -f PID-$1-$2 ]; then
        log "check_for_running has killed the hourly synchronization"
        break
    fi

    sleep 3595

    # if file is removed during sleeping and last synchronization is still running we stop here anyway
    if [ ! -f PID-$1-$2 ]; then
        log "check_for_running has killed the hourly synchronization"
        break
    fi
done

log "Wait for last synchronization..."
wait

log "...done."
eof

#cript="cd ${dest_folder}; counter=0; terminate=0; while [ 1 ]; do let counter=counter+1; nohup rsync -r -i -u -l ${src}/* ${dest_folder}/ > nohup_\${counter}.out 2>&1; if [ \`cat nohup_\${counter}.out | wc -l\` -eq 1 ]; then let terminate=terminate+1; fi; if [ \$terminate -gt ${timeout} ]; then break; fi; sleep 3600; done"

echo ssh -t ${user_at_dst} \"mkdir -p ${dst_folder}\"
echo ssh -t ${user_at_dst} \"screen -dSm \"rsync-$1-$2\" bash -c \"$script\"";" sleep 1\"

ssh -t ${user_at_dst} "mkdir -p ${dst_folder}"
scp local_sync_script.sh ${dest}/sync_script.sh
ssh -t ${user_at_dst} "chmod u+x ${dst_folder}/sync_script.sh"
ssh  ${user_at_dst} -t "cd ${dst_folder}; screen -dSm \"rsync-$1-$2\" bash -c ./sync_script.sh; sleep 1"
rm local_sync_script.sh