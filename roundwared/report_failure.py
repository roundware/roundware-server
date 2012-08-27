import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64

def send_email ():
	fromaddr = "roundwarnings@gmail.com"
	toaddrs = ["mike.machenry@gmail.com", "halsey@halseyburgund.com"]
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = ",".join(toaddrs)
	msg['Subject'] = "Round is down!"

	s = smtplib.SMTP("smtp.gmail.com", 587)
	s.ehlo()
	s.starttls()
	s.ehlo()
	s.login(fromaddr, "r0undmail")
	s.sendmail(fromaddr, toaddrs, msg.as_string())
	s.quit()

