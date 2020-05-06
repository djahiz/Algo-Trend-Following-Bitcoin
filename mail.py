"""
    Mail module
    ======================
  
    :Inputs:
 
       
    :Outputs:

 
"""
import smtplib

def send_mail(server, port, bot_mail, bot_passwd, email, message):
	s = smtplib.SMTP(server, port)

	s.starttls() 
	# Authentication 
	s.login(bot_mail, bot_passwd) 
	  
	# sending the mail 
	s.sendmail(bot_mail, email, message) 
	  
	# terminating the session 
	s.quit() 