import smtplib

smtp = smtplib.SMTP('localhost', 2500)
print smtp.ehlo('moon.localdomain')
print smtp.esmtp_features
print smtp.mail('Damien Churchill <damoxc@gmail.com>')
print smtp.rcpt('Damien Churchill <damoxc@damoxc.net>')
print smtp.data('Subject: Testing\n\nTest')
