#!/bin/bash
cd /data/sk1480/IOW_ESM/work/CCLM_Eurocordex
my_id=${OMPI_COMM_WORLD_RANK}
exec ./lmparbin > logfile_${my_id}.txt 2>&1