# Brenton Klassen
# 09/06/2014
# Email module with error handling

import settings
import smtplib
from email.mime.text import MIMEText

def sendmail(to, subject, body):

    msg = MIMEText(body)
    msg['To'] = to
    msg['Subject'] = subject
    msg['From'] = settings.get('mailfrom')

    # SMTP server settings
    user = settings.get('mailsmtpuser')
    pwd = settings.get('mailsmtppass')
    smtpserver = smtplib.SMTP(settings.get('mailsmtpserver'), settings.get('mailsmtpport'))
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(user, pwd)

    # send message
    try:
        smtpserver.send_message(msg)
    except:
        print('Message not sent...')
        
    smtpserver.quit()
