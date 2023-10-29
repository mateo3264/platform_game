# import smtplib

# # Import the email modules we'll need
# from email.mime.text import MIMEText

# # Open a plain text file for reading.  For this example, assume that
# # the text file contains only ASCII characters.
# #with open(textfile, 'rb') as fp:
#     # Create a text/plain message
#     # msg = MIMEText(fp.read())
# def send_mail():
#     msg = MIMEText('Prueba de email :D')

#     # me == the sender's email address
#     # you == the recipient's email address
#     msg['Subject'] = 'The contents of the email correando'
#     msg['From'] = 'maacostaro@unal.edu.co'
#     msg['To'] = 'mateohorcones@gmail.com'

#     # Send the message via our own SMTP server, but don't include the
#     # envelope header.
#     s = smtplib.SMTP('localhost')
#     s.sendmail('maacostaro@unal.edu.co', ['mateohorcones@gmail.com'], msg.as_string())
#     s.quit()


#vloj ddyd qsrw rtaw
from email.message import EmailMessage
import ssl
import smtplib

def send_mail(score):
    email_sender = 'mateohorcones@gmail.com'
    email_password = 'vloj ddyd qsrw rtaw'

    email_receiver = 'maacostaro@unal.edu.co'#'cosmecoffeeman@icloud.com'

    subject = 'Prueba de email :P'

    body = f'Your score is: {score}'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
