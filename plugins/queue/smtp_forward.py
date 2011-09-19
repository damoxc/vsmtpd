#
# queue/smtp_foward.py
#
# Copyright (C) 2011 Damien Churchill <damoxc@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.    If not, write to:
#   The Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor
#   Boston, MA    02110-1301, USA.
#
#

import smtplib
import logging

from vsmtpd.error import DenyError
from vsmtpd.hooks import hook
from vsmtpd.plugins.plugin import PluginBase

log = logging.getLogger(__name__)

class Plugin(PluginBase):

    def __init__(self, config):
        self.smtp_server = config.get('smtp_server')
        self.smtp_port = config.getint('smtp_port') or 25

    @hook
    def queue(self, transaction):
        log.info('forwarding to %s:%d', self.smtp_server, self.smtp_port)

        smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
        code, msg = smtp.mail(str(transaction.sender or ''))
        if code != 250:
            raise DenyError(msg)

        for rcpt in transaction.recipients:
            code, msg = smtp.rcpt(str(rcpt))
            if code != 250:
                raise DenyError(msg)

        code, msg = smtp.docmd('data')
        if code != 354:
            raise smtplib.SMTPDataError(code, msg)

        msg = transaction.body

        header = smtplib.quotedata(msg.headers.as_string())
        smtp.send(header)

        msg.seek(msg.body_start)
        for line in msg:
            smtp.send(smtplib.quotedata(line))

        smtp.send(smtplib.CRLF + '.' + smtplib.CRLF)
        code, msg = smtp.getreply()
        if code != 250:
            raise DenyError(msg)

        code, msg = smtp.quit()
        log.info('finished queueing')

        return True
