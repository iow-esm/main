# This script will fill the required files into the work directory for a CCLM model.
# This script is called from create_work_directories.R 

# read command line arguments
args = commandArgs(trailingOnly=TRUE)

# if command line arguments are incorrect, print usage
fail=FALSE
if (length(args)!=5) {
  fail=TRUE
} else {
  # read input arguments
  variable_table = args[1]
  new_grid = args[2]
  output_path = args[3]
  start_year = as.numeric(args[4])
  end_year = as.numeric(args[5])
}

if (fail) {
  print("usage: Rscript ./prepare_meteo_forcing_GETM.R variable_table new_grid output_path start_year end_year")
  print("variable_table = name of a file containing a table: getm_varname;getm_longname;getm_unit;orig_filename;orig_varname;orig_unit;unit_factor;unit_offset;comment")
  print("new_grid = 'keep' or the file name of a 'cdo remapbic' grid descripton file")
  print("output_path = path where output NetCDF files are stored")
  print("start_year = YYYY")
  print("end_year = YYYY")
  stop()
}

# read in variable table
variables = read.csv2(file=variable_table,header=TRUE,sep=";",stringsAsFactors=FALSE)

# loop over years
for (year in (start_year:end_year)) {
  # loop over variables
  for (i in seq_along(variables$getm_varname)) {
    # which variable do we have
    print(variables$orig_filename[i])
    # download or extract the correct year plus some overlap
    command=paste0("cdo -seldate,",year-1,"-12-30T00:00:00,",year+1,"-01-30T00:00:00 -selname,",variables$orig_varname[i]," ",variables$orig_filename[i]," ",output_path,"/temp1_",variables$getm_varname[i],".nc")
    print(command)
    system(command)
    if (new_grid=="keep") {
      command=paste0("mv ",output_path,"/temp1_",variables$getm_varname[i],".nc ",output_path,"/temp2_",variables$getm_varname[i],".nc")
    } else {
      command=paste0("cdo remapbic,",new_grid," ",output_path,"/temp1_",variables$getm_varname[i],".nc ",output_path,"/temp2_",variables$getm_varname[i],".nc")
    }
    print(command)
    system(command)
  }
}
