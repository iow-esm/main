import os
import glob

class MyAttemptHandler():
    """Class that handles your attempts.
    
    The name of the class is arbitrary

    Mandatory attributes: `next_attempt` which represents your next attempt, type must be convertable by str() function to string, typically a string or an integer, if all attempts are exhausted and you want to stop this must be set to None.
                                    
    Class can have arbitrarily more optional attributes. 
    However, all attributes must be serializable by the pickle library, see https://docs.python.org/3/library/pickle.html.
    The serialization into a file is necessary to store the state of the attempt handler over several jobs.
    IMPORTANT: If you want to start from scratch, you have to remove such files, which are sored as <run_name>_attempt_handler.obj in the root directory.

    Parameters can be arbitrary. In this example:

    :param root:        Path to the root directory
    :type root:         str     
        
    """
    
    def __init__(self, root = ".", input = "input"):  
    
        # initialize mandatory attribute self.next_attempt
        self.next_attempt = 0
    
        
        # optional arguments and members
        
        # it makes sense to memorize the root directory
        self.root = root     
        self.input = input

        self.parallelizations = {
            "MOM5_Baltic" : ["35.9x9", "132.14x18", "398.26x30", "877.36x39"],
            "CCLM_Eurocordex" : ["40.5x8", "192.8x24", "400.16x25", "875.25x35"]
        }

        # our maximal number of attempts
        self.max_attempts = len(self.parallelizations["MOM5_Baltic"])


    def prepare_input_files(self):
        
        # the first attempt has to be prepared manually to get the correct mappings and jobscript
        if self.next_attempt == 0:
            return

        model = "CCLM_Eurocordex"
        input_nml = self.root+"/input/"+self.input+"/"+model+"/INPUT_ORG"
        parallelization = self.parallelizations[model][self.next_attempt]  
        os.system("cp " + input_nml + "." + parallelization + " " + input_nml)

        model = "MOM5_Baltic"
        input_nml = self.root+"/input/"+self.input+"/"+model+"/input.nml"
        parallelization = self.parallelizations[model][self.next_attempt]
        os.system("cp " + input_nml + "." + parallelization + " " + input_nml)

        # create mappings
        os.system("cd "+self.root+"/scripts/prepare; python3 create_mappings.py "+self.input)

        # create jobscript
        os.system("cd "+self.root+"/scripts/prepare; python3 create_jobscript.py "+self.input)
        
    def prepare_attempt(self, **kwargs):
        r"""
        Mandatory method to prepare the attempt.
        
        Do whatever is necessary to set up the next attempt, e.g. manipulating input files.

        :Keyword Arguments:

        * **start_date** (*int*) --
          Start date of the current job in format YYYMMDD
        * **end_date** (*int*) --
          End date of the current job in format YYYMMDD  
                
        """     

        # Nothing to do here we prepare at the end of evaluation
        
        return

    def evaluate_attempt(self, crashed, **kwargs):
        r"""
        Mandatory method to evaluate the attempt.
        
        In this method the setting of the next_attempt should typically happen, e.g. incrementation.
        Important: If all attempts are exhausted, next_attempt must be set tot `None`.
        Important: If model has crashed, this function should return False otherwise following steps are ill-defined.

        :param crashed:         `True`, if the model has crashed, `False`, otherwise
        :type crashed:          bool   

        :Keyword Arguments:
        
        * **start_date** (*int*) --
          Start date of the current job in format YYYMMDD
        * **end_date** (*int*) --
          End date of the current job in format YYYMMDD          

        :return:                `True`, if attempt is accepted (work will be copied to output, hotstart folder is created), `False`, if attempt is not accepted (work will not be copied to output, no hotstart folder is created)      
        :rtype:                 bool
        """ 

        # you can use the keyword arguments
        start_date = kwargs["start_date"]
        end_date = kwargs["end_date"]
        print("Evaluating " + str(self.next_attempt) + " for start date " +  str(start_date) + " and end date " + str(end_date))

        # store the work directory for timings
        experiment_descriptor = "MOM5_Baltic-"+self.parallelizations["MOM5_Baltic"][self.next_attempt]+"-CCLM_Eurocordex-"+self.parallelizations["CCLM_Eurocordex"][self.next_attempt]
        output_directory = self.root+"/scaling_experiment/"+self.input+"/"+experiment_descriptor
        os.system("mkdir -p "+output_directory)
        os.system("cp -r "+self.root+"/work/"+self.input+"/* "+output_directory)    

        # if the model did succeed or crash, we want to go back but with different input files
        self.next_attempt += 1  

        # if we are done and can stop
        if self.next_attempt == self.max_attempts:
            self.next_attempt = None
            return False

        # prepare already here the next attempt to get correct jobscript and mappings
        # prepare input files for this attempt
        self.prepare_input_files()

        # we want to run the same month with all setups, thus we restart from the beginning
        return False

