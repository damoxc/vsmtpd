#
# vsmtpd/tests/common.py
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

import os
import collections

from unittest import TestCase as BaseTestCase
from vsmtpd.connection import Connection
from vsmtpd.daemon import Vsmtpd
from vsmtpd.transaction import Transaction
from vsmtpd.plugins.manager import PluginManager

class FakeSocket(object):

    def close(self):
        pass

    def getsockname(self):
        return ('127.0.0.1', 25)

    def makefile(self):
        pass

    def shutdown(self, how):
        pass

Options = collections.namedtuple('Options', 'config listen port')

def create_connection(**params):
    server = params['server'] if 'server' in params else create_daemon()
    sock = params['sock'] if 'sock' in params else FakeSocket()
    addr = params['addr'] if 'addr' in params else ('127.0.0.1', 34567)

    connection = Connection(server, sock, addr)
    for k, v in params.iteritems():
        if k == 'transaction':
            v['connection'] = connection
            connection._transaction = create_transaction(**v)

    return connection

def create_daemon(*args, **options):
    opts = {'config': None, 'listen': None, 'port': None}
    opts.update(options)
    return Vsmtpd(Options(**opts), args)

def create_transaction(**params):
    tranasction = Transaction(params.get('connection'))

    if 'recipients' in params:
        for rcpt in params['recipients']:
            transaction.add_recipient(rcpt)

    if 'sender' in params:
        transaction.sender = params['sender']

    if 'body' in params:
        tranasction.body.write(params['body'])

    return tranasction

class TestCase(BaseTestCase):
    pass

class PluginTestCase(TestCase):

    plugin_name = None

    def __init__(self, methodName='runTest'):
        super(PluginTestCase, self).__init__(methodName=methodName)
        dirname = os.path.dirname
        plugins = os.path.join(dirname(dirname(dirname(__file__))),
                               'plugins')
        manager = PluginManager([plugins])
        self.plugin = manager.load(self.plugin_name)
