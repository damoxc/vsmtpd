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
import errno
import gevent
import random
import hashlib
import logging

from email.message import Message
from email.header import Header
from email.utils import formatdate

from gevent import socket
from gevent import Timeout

from vsmtpd import error
from vsmtpd.address import Address
from vsmtpd.commands import parse as parse_command
from vsmtpd.transaction import Transaction
from vsmtpd.util import NoteObject

log = logging.getLogger(__name__)

def command(func):
    func._is_command = True
    return func

class Connection(NoteObject):
    """
    This class contains the majority of the logic behind the core of vsmtpd
    It handles interacting with the SMTP client and dispatching hook calls
    to the plugins.
    """

    @property
    def local_ip(self):
        """
        The IP address of the server connection.
        """
        return self._lip

    @property
    def local_host(self):
        """
        The hostname of the server connection.
        """
        return self._lhost

    @property
    def local_port(self):
        """
        The port of the server connection.
        """
        return self._lport

    @property
    def remote_ip(self):
        """
        The IP address of the remote client.
        """
        return self._rip

    @property
    def remote_host(self):
        """
        The hostname of the remote client.
        """
        return self._rhost

    @property
    def remote_port(self):
        """
        The port of the remote client.
        """
        return self._rport

    @property
    def hello(self):
        """
        Whether
        """
        return self._hello

    @property
    def hello_host(self):
        return self._hello_host

    @property
    def hostname(self):
        return self._config.get('helo_host') or self.local_host

    @property
    def relay_client(self):
        return self._relay_client

    @relay_client.setter
    def relay_client(self, value):
        self._relay_client = value

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
        self._server       = server
        self._config       = server.config
        self._socket       = sock
        self._file         = sock.makefile()
        self._rhost        = socket.getfqdn(self._rip)
        self._lhost        = socket.getfqdn(self._lip)
        self._timeout      = Timeout(30, error.TimeoutError)
        self._hello        = None
        self._hello_host   = ''
        self._relay_client = False
        self._connected    = True
        self._transaction  = None

        # Generate a unique identifier for this connection
        sha_hash = hashlib.sha1(self._rip)
        sha_hash.update(str(time.time()))
        sha_hash.update(str(random.getrandbits(64)))
        self._cid    = sha_hash.hexdigest()
        log.connection_id = self._cid[:7]

        # Add all the command controller methods
        self._commands = dict([(c, getattr(self, c)) for c in dir(self)
            if getattr(getattr(self, c), '_is_command', False)])

    def accept(self):
        log.info('Accepted connection from %s', self.remote_host)
        self.run_hooks('connect', self)
        self.send_code(220, self.greeting())

        while True:
            line = self.get_line()
            if not line:
                break

            parts = line.strip().split(None, 1)

            if not parts:
                self.send_syntax_error()
                continue

            # Dispatch the line into the server
            try:
                command = self._commands.get(parts[0].lower())
                if not command:
                    response = self.unknown(*parts)
                else:
                    response = command(parts[1] if parts[1:] else '')

            except Exception as e:
                log.exception(e)
                try:
                    self.disconnect(451, 'Internal error - try again later')
                finally:
                    break

            # Handle the response from the command
            try:
                code, msg, disconnect = response
            except (TypeError, ValueError):
                disconnect = False
                try:
                    code, msg = response
                except (TypeError, ValueError):
                    try:
                        code = int(response)
                    except (TypeError, ValueError):
                        log.error('Incorrect response from command: %r',
                                  response)
                        code = 451
                        msg = 'Internal error - try again later'
                        break

            if disconnect:
                try:
                    self.disconnect(code, msg)
                finally:
                    break
            else:
                self.send_code(code, msg)

        self._disconnect()

    @command
    def helo(self, line):
        msg = self.run_hooks('helo_parse', line)

        if self.hello:
            return 503, 'But you already said HELO...'

        try:
            self.run_hooks('helo', self, line)

        except error.HookError as e:
            if not (e.okay or e.done):
                return 450 if e.soft else 550, e.message, e.disconnect

            if not e.okay:
                return

        self._hello = 'helo'
        self._hello_host = line

        return (250, '%s Hi %s [%s]; I am so happy to meet you.' % (
                self.hostname, self.remote_host, self.remote_ip))

    @command
    def ehlo(self, line):
        msg = self.run_hooks('ehlo_parse', line)

        if self.hello:
            return 503, 'But you already said HELO...'

        try:
            self.run_hooks('ehlo', self, line)

        except error.HookError as e:
            if not (e.okay or e.done):
                return 450 if e.soft else 550, e.message, e.disconnect

            if not e.okay:
                return

        self._hello = 'ehlo'
        self._hello_host = line


        args = []
        size_limit = self._config.getint('size_limit')
        if size_limit:
            args.append('SIZE %d' % size_limit)

        return (250, '%s Hi %s [%s]; I am so happy to meet you.\n' % (
                self.hostname, self.remote_host, self.remote_ip) +
                '\n'.join(args))

    @command
    def mail(self, line):
        """
        This method handles the MAIL command in the SMTP transaction.

        :param line: The rest of the command line
        :type line: str
        """

        if not self.hello:
            return 503, "Manners? You haven't said hello..."

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
            addr, _params = parse_command('mail', line)
        except error.HookError as e:
            return 501, e.message or 'Syntax error in command'

        params = {}
        for param in _params:
            try:
                key, value = param.split('=')
            except:
                pass
            else:
                params[key.lower()] = value

        # Check to see if the reported message size is too large for us and delay early if so
        if 'size' in params:
            try:
                size = int(params['size'])
            except TypeError:
                size = 0

            size_limit = self.config.getint('size_limit')
            if self.hello == 'ehlo' and size_limit < size:
                log.info('Message too large to receive, declining')
                return 552, 'Message too big!'

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
            return 450 if e.soft else 550, e.message, e.disconnect

        log.info('getting from from %s', addr)
        tnx.sender = addr
        return (250,
                '%s sender OK - how exciting to get mail from you!' % addr)

    @command
    def rcpt(self, line):
        """
        This method handles the RCPT command parsing and checking of the
        recipient.

        :param line: The rest of the command line
        :type line: str
        """

        if not self.transaction and self.transaction.sender:
            return 503, 'Use MAIL before RCPT'

        log.info('full to_parameter: %s', line)

        try:
            addr, _params = parse_command('rcpt', line)
        except error.HookError as e:
            return 501, e.message or 'Syntax error in command'

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

        except error.StopHooksError as e:
            return

        except error.HookError as e:
            return (450 if e.soft else 550,
                    e.message or 'relaying denied',
                    e.disconnect)
        else:
            #if not msg:
            #    return self.send_code(450,
            #        'No plugin decided if relaying is allowed')

            self.transaction.add_recipient(addr)
            return 250, '%s, recipient ok' % addr

    @command
    def vrfy(self, line):
        try:
            message = self.run_hooks('vrfy')
        except error.DenyError as e:
            self.send_code(554, e.message or 'Access Denied')
            self.reset_transaction()
        else:
            if message:
                return 250, 'User OK' if message == True else message

            return (252,
                "Just try sending a mail and we'll see how it turns out...")

    @command
    def rset(self, line):
        self.reset_transaction()
        return 250, 'OK'

    @command
    def data(self, line):
        """
        This method handles the DATA command in the SMTP conversation.

        :param line: The rest of the command line
        :type line: str
        """
        try:
            message = self.run_hooks('data')
        except error.HookError as e:

            # A plugin handled receiving the data
            if e.done:
                return

            message = e.message or ('Message denied temporarily' if
                e.soft else 'Message denied')

            # Handle any denials
            if e.deny and e.soft and e.disconnect:
                return 421, message, True
            elif e.deny and e.soft:
                return 451, message
            elif e.deny:
                return 554, message, e.disconnect

        # Begin handling of receiving the message
        if not self.transaction.sender:
            return 503, 'MAIL first please'

        if not self.transaction.recipients:
            return 503, 'RCPT first please'

        self.send_code(354, 'go ahead')

        # Cancel the timeout
        self._timeout.cancel()

        buf = ''
        size = 0
        size_limit = self.config.getint('size_limit')
        in_header = True
        complete = False
        lines = 0

        body = self.transaction.body

        log.debug('size: %d / %d', size, size_limit)

        line = self.get_line()
        while line:
            # Check to see if it is the last line
            if line == '.\r\n':
                complete = True
                break

            lines += 1

            # Reject messages that have either bare LF or CR. Thanks to
            # qpsmtpd for this tip.
            if line == '.\n' or line == '.\r':
                return (421,
                    'See http://smtpd.develooper.com/barelf.html', True)

            # Increase the data size of this email
            size += len(line)

            # Check to make sure that no naughty clients ignored our size
            # advertisement at the beginning.
            if size_limit and size >= size_limit:
                self.reset_transaction()
                return 552, 'Message too big!'

            # Write the email data out to the spool
            body.write(line)

            # End the headers
            if in_header and line == '\r\n':
                in_header = False
                body.end_headers()

            log.debug('size: %d / %d', size, size_limit)

            line = self.get_line()

        # Connection is probably dead at this point
        if not complete:
            self.reset_transaction()
            return 451, 'Incomplete DATA'


        body.headers.insert_header(0, 'Received', self.received_line())

        try:
            self.run_hooks('data_post', self._transaction)
        except error.HookError as e:
            if e.done:
                return

            if e.soft:
                code = 452
                message = 'Message denied temporarily'
            else:
                code = 552
                message = 'Message denied'

            if not e.disconnect:
                self.reset_transasction()

            return code, message, e.disconnect

        return self.queue(self._transaction)

    def queue(self, transaction):
        """
        Handle the queuing of a message

        :param transaction: The transaction to queue
        :type transaction: :class:`vsmtpd.transaction.Transction`
        """

        try:
            self.run_hooks('queue_pre', self._transaction)
        except error.HookError as e:
            if e.done:
                return

        try:
            msg = self.run_hooks('queue', self._transaction)
        except error.HookError as e:
            if e.done:
                return

            if e.deny:
                code = 552
                message = e.message or 'Message denied'
            elif e.denysoft:
                code = 452
                message = e.message or 'Message denied temporarily'
            else:
                code = 451

        if not msg:
            return 451, 'Queuing declined or disabled; try again later'

        self.send_code(250, 'Queued' if msg is True else msg)

        try:
            self.run_hooks('queue_post', self._transaction)
        except error.HookError as e:
            if e.done:
                return

    @command
    def quit(self, line):
        msg = ''

        try:
            msg = self.run_hooks('quit', self)

        except error.HookError as e:
            if e.done:
                return self._disconnect()

            if e.message:
                msg = e.message
            else:
                msg = ''

        if not msg:
            msg = ('%s closing connection. Have a wonderful day.' %
                self.hostname)

        return 221, msg, True

    def unknown(self, command, *parts):
        try:
            result = self.run_hooks('unknown', self._transaction, command, *parts)
            if not result:
                return 500, 'Unrecognized command'
        except error.DenyDisconnectError as e:
            return 521, e.message, True
        except error.DenyError as e:
            return 500, e.message, True
        except error.HookError as e:
            if not e.done:
                return 500, 'Unrecognized command'

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
            if e.errno != errno.ENOTCONN:
                raise

        # Only set connected to False if the socket has been shutdown
        # correctly.
        self._connected = False

    def get_line(self):
        try:
            self._timeout.start()
            line = self._file.readline()

            # If there is a line we can return it
            if line:
                return line

            # If line is None then the client must have disconnected
            log.info('client disconnected')

        except socket.error as e:
            log.info('client disconnected')

        except error.TimeoutError:
            self.timeout()

        except Exception as e:
            log.exception(e)
            try:
                self.disconnect(451, 'Internal error - try again later')
            except:
                pass

        finally:
            self._timeout.cancel()

    def greeting(self):
        return '%s ESMTP' % self.local_host

    def kill(self):
        """
        This method can be used to kill the connection by killing the
        Greenlet it is running in, use cautiously as this isn't a nice
        way to disconnect clients and should only be used if the client
        has already disconnected.
        """
        gevent.getcurrent().kill(block=True)

    def reset_transaction(self):
        """
        Reset the message transaction and create a new one.
        """
        if self._transaction:
            self.run_hooks('reset_transaction')
        self._transaction = Transaction(self)

    def received_line(self):
        smtp = 'ESMTP' if self.hello == 'ehlo' else 'SMTP'
        return ('from %s (HELO %s) (%s)\n\tby %s (vsmtpd/0.1) with %s; %s' %
            (self.remote_host, self.hello_host, self.remote_ip,
            self.hostname, smtp, formatdate()))

    def run_hooks(self, hook_name, *args, **kwargs):
        return self._server.fire(hook_name, *args, **kwargs)

    def send_code(self, code, message='', *args):
        """
        Send a response back to the SMTP client.

        :param code: The response code to send
        :type code: int
        :keyword message: The message to send back
        :type message: str
        :param *args: format parameters
        """
        if message:
            message = message % args
        lines = message.splitlines()
        lastline = lines[-1:]
        for line in lines[:-1]:
            self.send_line('%3.3d-%s' % (code, line))
        self.send_line('%3.3d %s' % (code, lastline and lastline[0] or ''))

    def send_line(self, line):
        """
        Send a line back to the SMTP client.

        :param line: The line to send back to the client
        :type line: str
        """
        self._file.write(line + '\r\n')
        self._file.flush()
        log.info(line)

    def send_syntax_error(self):
        """
        Helper method for sending syntax errors
        """
        self.send_code(500, 'Error: bad syntax')

    def timeout(self):
        """
        Let the client know that they have exceeded their timeout and
        disconnect them.
        """
        log.info('Client exceeded timeout, disconnecting')
        self.disconnect(421,
            'Connection timeout, try talking faster next time.')
