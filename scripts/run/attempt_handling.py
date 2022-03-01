import os

class AttemptIterator:
    def __init__(self, attempt_handler):
        self.attempts = attempt_handler.attempts
        self.last_attempt_file = attempt_handler.last_attempt_file
        
    def get_next_attempt(self):
        
        # attempts must not be empty
        if self.attempts == []:
            print("List of attempts must not be empty!")
            return None
        
        # if there is no previous attempt, start with the first one
        if not os.path.isfile(self.last_attempt_file):
            return self.attempts[0]
            
        # read the last attempt
        try:
            if os.path.isfile(self.last_attempt_file):
                with open(self.last_attempt_file) as f:
                    last_attempt = f.readline()
                    f.close()
        except:
            print("Error while reading " + self.last_attempt_file)
            return None
        
        # try to find index of last attempt
        try:
            index = self.attempts.index(last_attempt)
        except:
            print("Content of " + self.last_attempt_file + " cannot be assigned to an attempt from " + str(self.attempts))
            return None
            
        # all attempts are exhausted
        if index == (len(self.attempts) - 1):
            print("All attempts are exhausted.")
            return None
        
        return self.attempts[index + 1]
    
    def store_last_attempt(self, last_attempt):
        
        # attempts are exhausted
        if last_attempt is None:
            return False
        
        try:
            # writing to file
            with open(self.last_attempt_file, "w") as f:
                f.writelines(last_attempt)
                f.close()
            return True
        
        except:
            print("Error while writing " + self.last_attempt_file)
            return False
