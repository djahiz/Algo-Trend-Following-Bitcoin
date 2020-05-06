"""
    Logs module
    ======================
  
    :Inputs:
 
       
    :Outputs:

 
"""
from datetime import datetime
import time

def print_logs(file, message):
	with open(file, "a") as f:
		f.writelines(str(datetime.fromtimestamp(time.time())) + " : " + message)