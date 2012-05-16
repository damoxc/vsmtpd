#
# vsmtpd/tests/test_connection.py
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

from gevent import socket
from cStringIO import StringIO
from vsmtpd.connection import command
from vsmtpd.connection import Connection
from vsmtpd.tests.common import TestCase

localhost = socket.getfqdn('127.0.0.1')

class Socket(object):

    def getsockname(self):
        return ('127.0.0.1', 25)

    def makefile(self):
        return StringIO()

class Server(object):

    config = {}

class ConnectionTestCase(TestCase):

    def setUp(self):
        self.socket = Socket()
        self.server = Server()
        self.connection = Connection(self.server, self.socket,
                                     ('127.0.0.1', 48765))

    def test_connection_decorator(self):
        @command
        def foo():
            pass
        self.assertTrue(foo._is_command)

    def test_connection_creation(self):
        connection = self.connection
        self.assertEqual(connection.local_ip, '127.0.0.1')
        self.assertEqual(connection.local_host, localhost)
        self.assertEqual(connection.local_port, 25)
        self.assertEqual(connection.remote_ip, '127.0.0.1')
        self.assertEqual(connection.remote_host, localhost)
        self.assertEqual(connection.remote_port, 48765)
        self.assertEqual(connection.transaction, None)

