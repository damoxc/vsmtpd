#
# vsmtpd/smtpd.py
#
# Copyright (C) 2010 Damien Churchill <damoxc@gmail.com>
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

from twisted.internet import reactor
from twisted.mail.smtp import ESMTP, SMTPFactory as _SMTPFactory

from vsmtpd.common import *
from vsmtpd.hooks import HookManager

class Connection(object):

    def __init__(self, transport):
        self.transport = transport

    @property
    def hello(self):
        return ''

    @property
    def hello_host(self):
        return ''

    @property
    def local_ip(self):
        return self.transport.getHost().host

    @property
    def local_port(self):
        return self.transport.getHost().port

    @property
    def remote_ip(self):
        return self.transport.getPeer().host

    @property
    def remote_port(self):
        return self.transport.getPeer().port

    @property
    def relay_client(self):
        return False

class SMTP(ESMTP):

    def makeConnection(self, transport):
        self.connection = Connection(transport)
        self.factory.hooks.dispatch_hook('pre_connection', self.connection)
        return ESMTP.makeConnection(self, transport)
    
    def connectionMade(self):
        self.factory.hooks.dispatch_hook('pre_connection', self.connection)
        return ESMTP.connectionMade(self)

    def connectionLost(self, reason):
        # run hook_post_connection
        return ESMTP.connectionLost(self, reason)

    def greeting(self):
        # run hook_greeting
        self.factory.hooks.dispatch_hook('greeting', self)
        return ESMTP.greeting(self)

    def do_HELO(self, rest):
        # run hook_helo
        return ESMTP.do_HELO(self, rest)

    def do_EHLO(self, rest):
        # run hook_ehlo
        return ESMTP.do_EHLO(self, rest)

    def validateFrom(self, helo, origin):
        # run hook_mail
        return ESMTP.validateFrom(self, helo, origin)

    def validateTo(self, user):
        # run hook_rcpt
        return ESMTP.validateTo(self, user)

    def do_UNKNOWN(self, rest):
        # run hook_unrecognized_command
        return ESMTP.do_UNKNOWN(self, rest)

    def do_DATA(self, rest):
        # run hook_data
        return ESMTP.do_DATA(self, rest)

    def do_RSET(self):
        # run hook_rset
        return ESMTP.do_RSET(self, rest)
    
    def do_QUIT(self, rest):
        # run hook_quit
        return ESMTP.do_QUIT(self, rest)

    def do_QUEUE(self):
        # run hook_pre_queue
        # run hook_queue
        # run hook_post_queue
        pass

class SMTPFactory(_SMTPFactory):

    def __init__(self, *args, **kwargs):
        _SMTPFactory.__init__(self, *args, **kwargs)
        self.protocol = SMTP

    def buildProtocol(self, addr):
        p = _SMTPFactory.buildProtocol(self, addr)
        p.factory = self
        return p

class SMTPD(object):

    def __init__(self):
        self.factory = SMTPFactory()
        self.factory.hooks = HookManager()

    def start(self):
        self.port = reactor.listenTCP(2500, self.factory)
