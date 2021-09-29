import os
import sys

def change_in_namelist(filename,              # file name to modify
                       after,                 # string after which we find the tag, e.g. "&input"
                       before="/",            # string that ends the namelist section
                       start_of_line="",      # typically the keyword
                       new_value="= .true.",  # string including the equals sign to which we change it
                       add_if_needed=False,   # if start_of_line is not found, add a line?
                       repeated=False,        # replace more than one occurence
                       completely_replace_line=False): # whether to remove the beginning of the line

    if not os.path.isfile(filename):
        print('ERROR in change_in_namelist: file '+filename+' does not exist and therefore cannot be modified.')
        sys.exit()
  
    # mask for leaving values unchanged (a value is something betwenn commas after an equal sign)
    mask = "_*_"
    # trim white spaces
    before = before.strip()
    start_of_line = start_of_line.strip()
    after = after.strip()
  
    # open the file for read and a new copy for write
    infile = open(filename,'r')
    outfile = open(filename+'_changed','w')
  
    # initialise status 
    status = 'too_early'
  
    # read the file line by line
    while True:
        line = infile.readline()
        if not line:
            break
        trimline = line.strip()

        # now decide by status what we are looking for
        if (status=='done')&(repeated==True):
            status='too_early'  # if we repeatedly replace, we start again if done
        if status=='here':
            if trimline[0:len(start_of_line)]==start_of_line:
                
                # if there is the mask in the new value, we have to consider the values individually
                if mask in new_value:
                    old_values = trimline.split("=")[1].split(",")
                    new_values = new_value.split("=")[1].split(",") 
                    
                    # build up substitute string
                    substitute = '='
                    for i,nv in enumerate(new_values):
                        # replace masked values with existing ones
                        if nv.strip() == mask:
                            new_values[i] = old_values[i]
                        
                        substitute += new_values[i]
                        
                        if i < (len(new_values) - 1):
                            substitute  += ','       
                # if there is no mask, take new values as is
                else:
                    substitute = new_value
                
                # replace value in this line
                if completely_replace_line:
                    line=substitute+'\n'
                else: 
                    line=start_of_line+substitute+'\n'
                status='done'
            if trimline[0:len(before)]==before:
                # section ended before line to replace was found
                # if desired, add the value
                outfile.write(start_of_line+new_value+'\n')
                status='done'
        if status=='too_early':
            if trimline[0:len(after)]==after:
                status = 'here'

        outfile.write(line)

    # closes the files
    infile.close()
    outfile.close()

    # move the new file to overwrite the old one
    os.replace(filename+'_changed',filename)
    return