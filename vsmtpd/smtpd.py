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

class SMTP(ESMTP):
    """
    Handles the basic ESMTP communication, firing off the hooks to
    allow plugins to extend any point of the smtp communication.
    """

    def disconnect(self, code, message='Good bye!'):
        """
        Handles performing DENY(|SOFT)_DISCONNECT, sending the appropriate
        response and disconnecting the client.

        :param code: The response code to send.
        :type code: int
        :keyword message: What to output after disconnecting
        :type message: str
        """
        self.dispatch('disconnect')
        self.sendCode(code, message)
        self.transport.loseConnection()

    def dispatch(self, hook_name, *args):
        """
        Proxy method to dispatch hooks and convert the response
        into a standard form.

        :param hook_name: The name of the hook
        :type hook_name: str
        """
        result = self.factory.hooks.dispatch(hook_name, *args)

        # Sanity check the result
        if isinstance(result, tuple):
            return result
        else:
            return (result, '')

    def makeConnection(self, transport):
        self.connection = Connection(transport)
        self.transaction = None

        (result, message) = self.dispatch('pre_connection', self.connection)

        # No plugin opted to take charge here, revert to default action
        if not result or result == DECLINED:
            return ESMTP.makeConnection(self, transport)

        if result == DENY_DISCONNECT:
            self.sendCode(550, message)
            self.loseConnection()
    
    def connectionMade(self):
        self.dispatch('connect', self.connection)
        return ESMTP.connectionMade(self)

    def connectionLost(self, reason):
        self.dispatch('post_connection', self.connection)
        return ESMTP.connectionLost(self, reason)

    def greeting(self):
        self.dispatch('greeting', self.connection)
        return ESMTP.greeting(self)

    def extensions(self):
        """
        Override the original extensions method, adding support for
        outputting the max message size allowed.
        """
        ext = ESMTP.extensions(self)
        if self.factory.max_size:
            ext['SIZE'] = [str(self.factory.max_size)]
        ext['8BITMIME'] = None
        return ext

    def do_HELO(self, rest):
        """
        Handle firing the helo hook. Setup the connection object
        """
        self.connection.hello = 'helo'
        self.connection.hello_host = rest
        self.dispatch('helo', self.connection)
        return ESMTP.do_HELO(self, rest)

    def do_EHLO(self, rest):
        """
        Handle firing the ehlo hook. Setup the connection object
        """
        self.connection.hello = 'ehlo'
        self.connection.hello_host = rest
        self.dispatch('ehlo', self.connection)
        return ESMTP.do_EHLO(self, rest)

    def validateFrom(self, helo, origin):
        self.dispatch('reset_transaction', self.connection, self.transaction)
        self.transaction = Transaction(self.connection)

        (result, message)  = self.dispatch('mail', self.transaction, origin)

        # No plugin opted to take charge here, revert to default action
        if not result:
            self.transaction.sender = origin
            return origin

        return ESMTP.validateFrom(self, helo, origin)

    def validateTo(self, user):
        (result, message) = self.dispatch('rcpt', self.transaction, user)

        # No plugin has taken charge here, perform default action.
        if not result:
            return ESMTP.validateTo(self, user)

    def do_UNKNOWN(self, command, rest):
        self.dispatch('unknown', self.transaction, command, rest)
        return ESMTP.do_UNKNOWN(self, rest)

    def do_DATA(self, rest):
        self.dispatch('data', self.transaction)
        return ESMTP.do_DATA(self, rest)

    def do_RSET(self, rest):
        # We don't care what plugins think about this for now
        self.dispatch('reset_transaction', self.connection, self.transaction)

        # Reset the transaction like we've been told
        self.transaction = Transaction(self.connection)

        # Let twisted handle the rest
        return ESMTP.do_RSET(self, rest)
    
    def do_QUIT(self, rest):
        self.dispatch('quit', self.connection)
        return ESMTP.do_QUIT(self, rest)

    def do_QUEUE(self):
        # run hook_pre_queue
        # run hook_queue
        # run hook_post_queue
        pass

    def state_COMMAND(self, line):
        line = line.strip()

        parts = line.split(None, 1)
        if parts:
            method = self.lookupMethod(parts[0]) or self.do_UNKNOWN
            if method is self.do_UNKNOWN:
                if len(parts) == 2:
                    method(parts[0], parts[1])
                else:
                    method(parts[0], '')
            else:
                if len(parts) == 2:
                    method(parts[1])
                else:
                    method('')
        else:
            self.sendSyntaxError()

    def _cbFromValidate(self, from_, code=250,
        msg='sender OK - how exciting to get mail from you!'):
        """
        Override _cbFromValidate so we can format the response to MAIL
        how we want to.
        """
        self._from = from_
        self.sendCode(code, '<%s>, %s' % (from_, msg))

class SMTPFactory(_SMTPFactory):

    protocol = SMTP

    def buildProtocol(self, addr):
        p = _SMTPFactory.buildProtocol(self, addr)
        p.factory = self
        return p

    @property
    def config(self):
        return self.smtpd.config

    @property
    def hooks(self):
        return self.smtpd.hooks

    @property
    def plugins(self):
        return self.smtpd.plugins

class SMTPD(object):

    def __init__(self):
        self.factory = SMTPFactory()
        self.factory.smtpd = self
        self.factory.hooks = HookManager()
        self.factory.max_size = 26214400
        self.interfaces = None
        self.port = 25

    def start(self):
        self.port = reactor.listenTCP(self.port, self.factory)
