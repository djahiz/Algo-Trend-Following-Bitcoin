"""
    Mail module
    ======================
  
    :Inputs:
 
       
    :Outputs:

 
"""
import smtplib
from logs import *
from settings import *

def send_mail(server, port, bot_mail, bot_passwd, email, message):
	try:
		s = smtplib.SMTP(server, port)

		s.starttls() 
		# Authentication 
		s.login(bot_mail, bot_passwd) 
		  
		# sending the mail
		s.sendmail(bot_mail, email, message)

		# terminating the session 
		s.quit()
	except Exception as e:
		print_logs(LOG_ERROR, "An error occurred when sending mail " + str(e.args[0]))
		pass
	