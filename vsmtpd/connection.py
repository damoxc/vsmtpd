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

import logging

from gevent import Greenlet, Timeout, socket

from vsmtpd.error import TimeoutError

log = logging.getLogger(__name__)

COMMAND, DATA, AUTH = 'COMMAND', 'DATA', 'AUTH'

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
        return self._rort

    @property
    def hello(self):
        return self._hello

    @property
    def hello_host(self):
        return self._hello_host

    @property
    def relay_client(self):
        return self._relay_client

    def __init__(self, server, sock, address):
        (self._rip, self._rport) = address
        (self._lip, self._lport) = sock.getsockname()
        self._server = server
        self._socket = sock
        self._file   = sock.makefile()
        self._rhost  = socket.getfqdn(self._rip)
        self._lhost  = socket.getfqdn(self._lip)
        self._timeout = Timeout(30, TimeoutError)
        self._hello = None
        self._hello_host = ''
        self._relay_client = False
        self._mode = COMMAND
        self._modefunc = self.state_COMMAND
        self._connected = True

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

                self._modefunc(line)
            except socket.error as e:
                log.info('Client disconnected')
                break

            except TimeoutError:
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

    def state_COMMAND(self, line):
        line = line.strip()
        parts = line.split(None, 1)

        if not parts:
            return self.send_syntax_error()

        method = self.lookup_method(parts[0])
        if method:
            if len(parts) == 2:
                method(parts[1])
            else:
                method('')
        else:
            if len(parts) == 2:
                self.do_UNKNOWN(method, parts[1])
            else:
                self.do_UNKNOWN(method, '')

    def state_DATA(self, line):
        pass

    def state_AUTH(self, line):
        pass

    def do_UNKNOWN(self, method, rest):
        self.send_code(500, 'Command not implemented')

    def do_HELO(self, rest):
        self._hello = 'hello'
        self._hello_host = rest
        self._transaction = Transaction(self)
        self.fire('helo', self)

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

    def fire(self, hook_name, *args, **kwargs):
        return self._server.fire(hook_name, *args, **kwargs)

    def lookup_method(self, command):
        return getattr(self, 'do_' + command.upper(), None)

    def send_code(self, code, message=''):
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
