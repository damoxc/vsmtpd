import sys
import smtplib

def output((code, msg)):
    sys.stdout.write('%s %s\n' % (code, msg))
    sys.stdout.flush()

smtp = smtplib.SMTP('localhost', 2500)
output(smtp.ehlo('moon.localdomain'))
print smtp.esmtp_features
output(smtp.mail('Damien Churchill <damoxc@gmail.com>'))
output(smtp.rcpt('Damien Churchill <damoxc@damoxc.net>'))
output(smtp.data('Subject: Testing\n\nTest'))
output(smtp.quit())
