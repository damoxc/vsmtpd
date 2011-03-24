#
# vsmtpd/daemon.py
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
import vsmtpd.logging_setup

from gevent.pool import Pool
from gevent.server import StreamServer
from optparse import OptionParser

from vsmtpd.config import load_config
from vsmtpd.connection import Connection
from vsmtpd.hooks import HookManager

log = None
vsmtpd = None

class Vsmtpd(object):

    def __init__(self, options, args):
        self.options = options
        self.args = args
        self.pool = None

        # Load the configuration for the server
        self.load_config()

        connection_limit = self.config.getint('vsmtpd', 'connection_limit')
        if connection_limit:
            self.pool = Pool(connection_limit)
            log.info('Limiting connections to %d', connection_limit)

        # Load the plugins
        for section in self.config.sections():
            if not section.startswith('plugin:'):
                continue
            plugin = section.split(':', 1)[1]

        self.hook_manager = HookManager()

    def fire(self, hook_name, *args, **kwargs):
        return self.hook_manager.dispatch_hook(hook_name, *args, **kwargs)

    def handle(self, socket, address):
        connection = Connection(self, socket, address)
        connection.run_hooks('pre_connection', connection)
        connection.accept()
        connection.run_hooks('disconnect', connection)

    def load_config(self):
        self.config = load_config(self.options.config or 'vsmtpd.cfg', {
            'vsmtpd': {
                'port': 25,
                'interface': None,
                'size_limit': None,
                'smtp_helo_host': None,
                'connection_limit': 100,
                'spool_dir': '/var/spool/vsmtpd',
                'keyfile': None,
                'certfile': None,
                'cert_reqs': None,
                # FIXME: Provide a default secure (SSLV3/TLSV1) cipher setup
                'ssl_version': None,
                'ca_certs': None,
                'suppress_ragged_eofs': None,
                'do_handshake_on_connect': None,
                # FIXME: Provide a default secure (SSLV3/TLSV1) cipher setup
                'ciphers': None
            }
        })

    def start(self):
        log.info('Starting server on 0.0.0.0 port 2500')
        self.server = StreamServer(('0.0.0.0', 2500), self.handle,
            spawn=self.pool)
        self.server.serve_forever()

def main():
    global log, vsmtpd

    parser = OptionParser()
    parser.add_option('-c', '--config', dest='config', action='store',
        default=None, help='the configuration file to use')
    parser.add_option('-l', '--listen', dest='listen',  action='append',
        help='listen on this address')
    parser.add_option('-p', '--port', dest='port', type='int', default=25,
        help='set the default port to listen on')
    (options, args) = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format = '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] [%(conn_id)s] %(message)s',
        datefmt = '%a %d %b %Y %H:%M:%S'
    )

    log = logging.getLogger(__name__)
    log.connection_id = 'master'

    vsmtpd = Vsmtpd(options, args)
    try:
        vsmtpd.start()
    except KeyboardInterrupt:
        #from guppy import hpy
        #h = hpy()
        #print h.heap()
        pass
