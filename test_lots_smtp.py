import gevent
from gevent import monkey
monkey.patch_all()

import smtplib

def send_test_msg():
    smtp = smtplib.SMTP('localhost', 2500)
    try:
        smtp.sendmail('test@example.com', 'dave@example.com', """Subject: Testing
From: <test@example.com>
To: <john@example.com>

This is a test ja?!""")
    except:
        pass

while True:
    jobs = [gevent.spawn(send_test_msg) for i in xrange(0, 250)]
    gevent.joinall(jobs)
