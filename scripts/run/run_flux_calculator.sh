#!/bin/bash
cd /data/sk1480/IOW_ESM/work/flux_calculator
my_id=${OMPI_COMM_WORLD_RANK}
exec ./flux_calculator > logfile_${my_id}.txt 2>&1