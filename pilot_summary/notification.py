import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from os.path import basename

COMMASPACE = ', '

def send_email(smtp_server, sender, mailing_list, subject, attachment):
  assert isinstance(mailing_list, list)
  #
  msg = MIMEMultipart()
  msg['From'] = sender
  msg['To'] = COMMASPACE.join(mailing_list)
  msg['Date'] = formatdate(localtime=True)
  msg['Subject'] = subject
  # msg.attach(MIMEText(text))
  with open(attachment, "rb") as attachment_file:
    part = MIMEApplication(
      attachment_file.read(),
      Name=basename(attachment)
    )
  #
  part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment)
  msg.attach(part)
  smtp = smtplib.SMTP(smtp_server)
  smtp.sendmail(sender, mailing_list, msg.as_string())
  smtp.close()
