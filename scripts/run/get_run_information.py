import glob

def get_run_information(IOW_ESM_ROOT, debug_mode = False):
    
    info_files_description = {}
    
    if debug_mode:
        info_files_description[IOW_ESM_ROOT + "/LAST_BUILD_debug"] = "*** Model built in debug mode with" 
    else:
        info_files_description[IOW_ESM_ROOT + "/LAST_BUILD_release"] = "*** Model built in release mode with"
        
    info_files_description[IOW_ESM_ROOT + "/LAST_DEPLOYED_SETUPS"]  = "*** Last deployed setups"
    info_files_description[IOW_ESM_ROOT + "/SETUP_INFO"] = "*** Setup info"
    
    info_files_description[IOW_ESM_ROOT + "/input/global_settings.py"] = "*** Global settings"
                            
    info = ""
    for pattern, description in info_files_description.items():
        file_names = glob.glob(pattern)
        for fn in file_names:
            info += description + " (" + fn + "):\n"
            info += "\n"
            with open(fn, 'r') as file:
                info += file.read()
            file.close()
            info += "\n"
            info += "\n"
            
    return info