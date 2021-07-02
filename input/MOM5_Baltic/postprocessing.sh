#!/bin/bash

# at HLRN
# d=/sw/local/packages/mppncombine/large_files_2012.04.26/
d="/home/b/mvxsbrun/mom_coupling_ori/src/postprocessing/mppnccombine/"
#d="/work/thomas/ModelCode/MOM511/mom/src/postprocessing/mppnccombine/"
export YEAR=$1

${d}mppnccombine -n4 -d 3 -m       -r gridinfo_${YEAR}.nc gridinfo_${YEAR}_02.nc.0???

for m in {1..12}
do
if [ $m -lt 10 ]; then
${d}mppnccombine -n4 -d 3 -m -k 11 -r ocean_day3d_${YEAR}_0${m}.nc ocean_day3d_${YEAR}_0${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r atmos_day_${YEAR}_0${m}.nc atmos_day_${YEAR}_0${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ice_day_${YEAR}_0${m}.nc ice_day_${YEAR}_0${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ocean_day2d_${YEAR}_0${m}.nc ocean_day2d_${YEAR}_0${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 22 -r ocean_trps_${YEAR}_0${m}.nc ocean_trps_${YEAR}_0${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ergom_flux3d_${YEAR}_0${m}.nc ergom_flux3d_${YEAR}_0${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ergom_flux_surf_${YEAR}_0${m}.nc ergom_flux_surf_${YEAR}_0${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ergom_flux_sed_${YEAR}_0${m}.nc ergom_flux_sed_${YEAR}_0${m}.nc.0???
else
${d}mppnccombine -n4 -d 3 -m -k 11 -r ocean_day3d_${YEAR}_${m}.nc ocean_day3d_${YEAR}_${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r atmos_day_${YEAR}_${m}.nc atmos_day_${YEAR}_${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ice_day_${YEAR}_${m}.nc ice_day_${YEAR}_${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ocean_day2d_${YEAR}_${m}.nc ocean_day2d_${YEAR}_${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 22 -r ocean_trps_${YEAR}_${m}.nc ocean_trps_${YEAR}_${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ergom_flux3d_${YEAR}_${m}.nc ergom_flux3d_${YEAR}_${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ergom_flux_surf_${YEAR}_${m}.nc ergom_flux_surf_${YEAR}_${m}.nc.0???
${d}mppnccombine -n4 -d 3 -m -k 11 -r ergom_flux_sed_${YEAR}_${m}.nc ergom_flux_sed_${YEAR}_${m}.nc.0???
fi
done
