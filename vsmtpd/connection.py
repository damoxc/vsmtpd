#
# vsmtpd/connection.py
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

import time
import hashlib
import logging

from gevent import Greenlet, Timeout, socket
from vsmtpd import error, commands, hooks

from vsmtpd.address import Address

log = logging.getLogger(__name__)

def command(func):
    func._is_command = True
    return func

class Transaction(object):

    @property
    def connection(self):
        return self._connection

    @property
    def body_filename(self):
        """
        Returns the temporary filename used to store the message contents;
        useful for virus scanners so that an additional copy doesn't need
        to be made.

        Calling `body_filename` also forces spooling to disk. A message is
        not spooled to disk if it's size is smaller than
        config['size_threshold'], default threshold is 0, the sample config
        file sets this to 10000.
        """
        pass

    @property
    def data_size(self):
        return 0

    @property
    def recipients(self):
        return self._recipients

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        self._sender = value
        return self._sender
    
    def __init__(self, connection):
        self._connection = connection
        self._recipients = []
        self._sender     = None

    def add_recipient(self, recipient):
        pass

    def remove_recipient(self, recipient):
        pass

class Connection(object):

    @property
    def local_ip(self):
        return self._lip

    @property
    def local_host(self):
        return self._lhost

    @property
    def local_port(self):
        return self._lport

    @property
    def remote_ip(self):
        return self._rip

    @property
    def remote_host(self):
        return self._rhost

    @property
    def remote_port(self):
        return self._rport

    @property
    def hello(self):
        return self._hello

    @property
    def hello_host(self):
        return self._hello_host

    @property
    def relay_client(self):
        return self._relay_client

    @property
    def config(self):
        return self._config

    @property
    def transaction(self):
        return self._transaction

    @property
    def id(self):
        return self._cid

    def __init__(self, server, sock, address):
        self._rip, self._rport = address
        self._lip, self._lport = sock.getsockname()
        self._server = server
        self._config = server.config
        self._socket = sock
        self._file   = sock.makefile()
        self._rhost  = socket.getfqdn(self._rip)
        self._lhost  = socket.getfqdn(self._lip)
        self._timeout = Timeout(30, error.TimeoutError)
        self._hello = None
        self._hello_host = ''
        self._relay_client = False
        self._connected = True
        self._transaction = None

        # Generate a unique identifier for this connection
        sha_hash = hashlib.sha1(self._rip)
        sha_hash.update(str(time.time()))
        self._cid    = sha_hash.hexdigest()
        log.connection_id = self._cid[:7]

        # Add all the command controller methods
        self._commands = dict([(c, getattr(self, c)) for c in dir(self)
            if getattr(getattr(self, c), '_is_command', False)])


    def accept(self):
        log.info('Accepted connection from %s', self.remote_host)
        self.send_code(220, self.greeting())

        while True:
            try:
                self._timeout.start()
                line = self._file.readline()
                if not line:
                    log.info('Client disconnected')
                    break

                line = line.strip()
                parts = line.split(None, 1)

                if not parts:
                    self.send_syntax_error()
                    continue

                command = self._commands.get(parts[0].lower())
                if not command:
                    self.run_hooks('unknown', self._transaction, *parts)
                    continue

                command(parts[1] if parts[1:] else '')

            except socket.error as e:
                log.info('Client disconnected')
                break

            except error.TimeoutError:
                self.timeout()
                break

            except Exception as e:
                log.exception(e)
                try:
                    self.disconnect(451, 'Internal error - try again later')
                finally:
                    break

            finally:
                self._timeout.cancel()

        self._disconnect()

    @command
    def helo(self, line):
        msg = self.run_hooks('helo_parse', line)

        if self.hello:
            return self.send_code(503, 'But you already said HELO...')

        try:
            self.run_hooks('helo', line)

        except error.StopHooks:
            return

        except error.HookError as e:
            self.send_code(450 if e.soft else 550, e.message)
            if e.disconnect:
                self._disconnect()
            return

        self._hello = 'helo'
        self._hello_host = line
        self.send_code(250, '%s Hi %s [%s]; I am so happy to meet you.' %
            (self.config.get('me'), self.remote_host, self.remote_ip))

    @command
    def ehlo(self, line):
        msg = self.run_hooks('ehlo_parse', line)

        if self.hello:
            return self.send_code(503, 'But you already said HELO...')

        try:
            self.run_hooks('ehlo', line)

        except error.StopHooks:
            return

        except error.HookError as e:
            self.send_code(450 if e.soft else 550, e.message)
            if e.disconnect:
                self._disconnect()
            return

        self._hello = 'ehlo'
        self._hello_host = line

        args = []
        if 'sizelimit' in self._config:
            args.append('SIZE %s' % self._config.get('sizelimit'))

        self.send_code(250, '%s Hi %s [%s]; I am so happy to meet you.\n' %
            (self._config.get('me'), self.remote_host, self.remote_ip)
            + '\n'.join(args))

    @command
    def mail(self, line):
        """
        This method handles the MAIL command in the SMTP transaction.

        :param line: The rest of the command line
        :type line: str
        """

        if not self.hello:
            return self.send_code(503, "Manners? You haven't said hello...")
        
        self.reset_transaction()
        log.info('full from_parameter: %s', line)

        # Disable until more operational, parsing hooks will be the last
        # hooks implemented.
        #
        #try:
        #    (from_addr, params) = self.run_hooks('mail_parse', line)
        #except error.HookError as e:
        #    self.send_syntax_error()
        #except Exception as e:
        #    pass
        #else:
        #    pass
        try:
            addr, _params = commands.parse('mail', line)
        except error.HookError as e:
            self.send_code(501, e.message or 'Syntax error in command')
            return

        params = {}
        for param in _params:
            try:
                key, value = param.split('=')
            except:
                pass
            else:
                params[key.lower()] = value

        tnx = self.transaction
        try:
            addr = self.run_hooks('mail_pre', tnx, addr, params) or addr
        except error.HookError as e:
            pass

        log.debug('from email address: [%s]', addr)

        # Turn addr into an Address object now
        addr = Address(addr)

        try:
            msg = self.run_hooks('mail', tnx, addr, params)
        except error.HookError as e:
            self.send_code(450 if e.soft else 550, e.message)
            if e.disconnect:
                self._disconnect()
            return

        log.info('getting from from %s', addr)
        self.send_code(250,
            '%s sender OK - how exciting to get mail from you!', addr)
        tnx.sender = addr

    @command
    def rcpt(self, line):
        """
        This method handles the RCPT command parsing and checking of the
        recipient.

        :param line: The rest of the command line
        :type line: str
        """

        if not self.transaction.sender:
            return self.send_code(503, 'Use MAIL before RCPT')
        
        log.info('full to_parameter: %s', line)

        try:
            addr, _params = commands.parse('rcpt', line)
        except error.HookError as e:
            self.send_code(501, e.message or 'Syntax error in command')
            return

        #msg = self.run_hooks('rcpt_parse', line)

        params = {}
        for param in _params:
            try:
                key, value = param.split('=')
            except:
                pass
            else:
                params[key.lower()] = value

        tnx = self.transaction
        try:
            addr = self.run_hooks('rcpt_pre', tnx, addr) or addr
        except error.HookError as e:
            pass

        log.debug('to email address: [%s]', addr)

        try:
            msg = self.run_hooks('rcpt', tnx, addr)
        except error.HookError as e:
            self.send_code(450 if e.soft else 550, e.message)
            if e.disconnect:
                self._disconnect()
            return

        self.send_code(450, 'No plugin decided if relaying is allowed')

    @command
    def vrfy(self, line):
        self.run_hooks('vrfy')

    @command
    def rset(self, line):
        self.send_code(250, 'OK')

    @command
    def quit(self, line):
        msg = ''
        
        try:
            msg = self.run_hooks('quit')

        except error.HookError as e:
            if isinstance(e, error.StopHooks):
                self._disconnect()
                return

            if e.message:
                msg = e.message
            else:
                msg = ''

        if not msg:
            msg = ('%s closing connection. Have a wonderful day.' % 
                self._config.get('me'))

        self.disconnect(221, msg)

    def do_UNKNOWN(self, method, rest):
        self.fire('unknown', self.transaction, method, rest)

    def respond_UNKNOWN(self, transaction, method, rest):
        self.send_code(500, 'Command not implemented')

    def disconnect(self, code, message=''):
        """
        Disconnects the client in a timely fashion. Sending the client a
        message prior to disconnection.

        :param code: The code to send
        :type code: int
        :keyword message: The message to send the client
        :type message: str
        """

        self.send_code(code, message)
        self._disconnect()

    def _disconnect(self):
        """
        Disconnects the socket in a timely fashion.
        """
        # Nothing to do if we're already disconnected
        if not self._connected:
            return

        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except socket.error as e:
            if e.errno == 107:
                pass
            else:
                raise
        # Only set connected to False if the socket has been shutdown
        # correctly.
        self._connected = False

    def greeting(self):
        return '%s ESMTP' % self.local_host

    def reset_transaction(self):
        if self._transaction:
            self.run_hooks('reset_transaction')
        self._transaction = Transaction(self)

    def run_hooks(self, hook_name, *args, **kwargs):
        return None
        return self._server.fire(hook_name, *args, **kwargs)

    def send_code(self, code, message='', *args):
        if message:
            message = message % args
        lines = message.splitlines()
        lastline = lines[-1:]
        for line in lines[:-1]:
            self.send_line('%3.3d-%s' % (code, line))
        self.send_line('%3.3d %s' % (code, lastline and lastline[0] or ''))

    def send_line(self, line):
        self._file.write(line + '\r\n')
        self._file.flush()

    def send_syntax_error(self):
        self.send_code(500, 'Error: bad syntax')

    def timeout(self):
        log.info('Client exceeded timeout, disconnecting')
        self.disconnect(421,
            'Connection timeout, try talking faster next time.')
