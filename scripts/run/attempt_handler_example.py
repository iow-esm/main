import os

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
    
    def __init__(self, root = "."):  
    
        # initialize mandatory attribute self.next_attempt
        self.next_attempt = 1
    
        
        # optional arguments and members
        
        # it makes sense to memorize the root directory
        self.root = root     
        
        # our maximal number of attempts
        self.max_attempts = 4
        
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

        # you can use the keyword arguments
        start_date = kwargs["start_date"]
        end_date = kwargs["end_date"]
        print("Peparing " + str(self.next_attempt) + " for start date " +  str(start_date) + " and end date " + str(end_date))
        
        # copy some prepared files to the actual input file
        input_nml = self.root + "/input/MOM5_Baltic/input.nml"
        os.system("cp " + input_nml + "." + str(self.next_attempt) + " " + input_nml)
        
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

        # if the model has crashed, react here
        if crashed:
            
            # we have no attempts left, we should stop here
            if self.next_attempt == self.max_attempts:
                self.next_attempt = None
                return False
            
            # there are attempts left, go to the next set of input files 
            self.next_attempt += 1
            # throw away work of failed attempt (you might also store it somewhere for debugging)
            return False
            
        # if the model did succeed, we can go back to the previous input files
        if self.next_attempt > 1:
            self.next_attempt -= 1                
            
        return True
