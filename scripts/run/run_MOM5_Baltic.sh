#!/bin/bash
cd /data/sk1480/IOW_ESM/work/MOM5_Baltic
my_id=${OMPI_COMM_WORLD_RANK}
exec ./fms_MOM_SIS.x > logfile_${my_id}.txt 2>&1