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

import os
import sys
import gevent
import signal
import logging
import vsmtpd.logging_setup

from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer
from optparse import OptionParser

from vsmtpd.config import load_config
from vsmtpd.config import ConfigWrapper
from vsmtpd.connection import Connection
from vsmtpd.hooks import HookManager
from vsmtpd.plugins.manager import PluginManager
from vsmtpd.util import set_cmdline

log = None
vsmtpd = None

class Vsmtpd(object):

    def __init__(self, options, args):
        self.options = options
        self.args = args
        self.pool = None
        self.workers = []

        # Load the configuration for the server
        self.load_config()

        # If we positive connection limit create a Pool with that limit
        connection_limit = self.config.getint('connection_limit')
        if connection_limit > 0:
            self.pool = Pool(connection_limit)
            log.info('Limiting connections to %d', connection_limit)

        # Create the hook manager
        self.hook_manager = HookManager()

        # Create the plugin manager
        plugin_path = self.config.get('plugin_path').split(':')
        self.plugin_manager = PluginManager(plugin_path)

    def fire(self, hook_name, *args, **kwargs):
        return self.hook_manager.dispatch_hook(hook_name, *args, **kwargs)

    def handle(self, socket, address):
        connection = Connection(self, socket, address)
        connection.run_hooks('pre_connection', connection)
        connection.accept()
        connection.run_hooks('post_connection', connection)

    def load_config(self):
        self._config = load_config(self.options.config or 'vsmtpd.cfg', {
            'vsmtpd': {
                'port': 25,
                'interface': None,
                'backlog': 50,
                'workers': 0,
                'size_limit': 0,
                'helo_host': None,
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
                'ciphers': None,
                'plugin_path': '/usr/share/vsmtpd/plugins'
            }
        })
        self.config = ConfigWrapper(self._config, 'vsmtpd')

    def load_plugins(self):
        log.info('Loading plugins...')
        # Load the plugins
        for section in self._config.sections():
            if not section.startswith('plugin:'):
                continue
            plugin_name = section.split(':', 1)[1]
            try:
                plugin_cls = self.plugin_manager.load(plugin_name)
            except Exception as e:
                log.fatal("Failed to load plugin '%s'", plugin_name)
                log.exception(e)
                exit(1)

            try:
                if self._config.options(section):
                    plugin = plugin_cls(ConfigWrapper(self._config, section))
                else:
                    plugin = plugin_cls()
                plugin.plugin_name = plugin_name
            except Exception as e:
                log.fatal("Failed to initialise plugin '%s'", plugin_Name)
                log.exception(e)
                exit(1)

            self.hook_manager.register_object(plugin)

    def reload(self):
        """
        Reload the configuration.
        """

    def start(self):
        """
        Starts the vsmtpd server in either master or worker mode.
        """

        # Install the signal handlers
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGHUP, self.reload)
        signal.signal(signal.SIGINT, self.stop)

        workers = self.config.getint('workers')
        backlog = self.config.getint('backlog')

        addr = ('0.0.0.0', 2500)

        if backlog < 1:
            backlog = 50

        log.info('Starting server on %s port %d', *addr)

        if workers <= 0:
            set_cmdline('vsmtpd: master')
            self._start(addr, backlog)

        # Open the socket for master/worker operation.
        self.sock = socket.socket()
        self.sock.bind(addr)
        self.sock.listen(backlog)
        self.sock.setblocking(0)

        # Spawn the worker servers
        for i in xrange(0, workers):
            self._start_slave()

        # Set the process title
        set_cmdline('vsmtpd: master')

        # Wait for the children to die
        os.waitpid(-1, 0)

    def _start(self, listener, backlog=None):
        """
        Starts the vsmtpd server.
        """

        self.server = StreamServer(listener, self.handle, backlog=backlog,
            spawn=self.pool)
        self.server.serve_forever()

    def _start_slave(self):
        """
        Starts a new slave worker process.
        """
        pid = os.fork()
        if pid == 0:
            # Set up the command line and logger id
            set_cmdline('vsmtpd: worker')
            log.connection_id = 'worker'

            # Call event_reinit()
            gevent.reinit()

            # Start vsmtpd
            self._start(self.sock)
        else:
            log.info('Worker spawned PID %d', pid)
            self.workers.append(pid)

    def stop(self, *args):
        """
        Shuts down the vsmtpd server and any workers running.
        """
        # Shut down the server or the socket, depending on which is running
        if self.workers:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            for pid in self.workers:
                os.kill(pid, signal.SIGTERM)
        else:
            self.server.stop()

        # Finally exit successfully
        sys.exit()

def main():
    global log, vsmtpd

    parser = OptionParser()
    parser.add_option('-c', '--config', dest='config', action='store',
        default=None, help='the configuration file to use')
    parser.add_option('-l', '--listen', dest='listen',  action='append',
        help='listen on this address')
    parser.add_option('-p', '--port', dest='port', type='int', default=None,
        help='set the default port to listen on')
    (options, args) = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format = '%(asctime)s %(levelname)s [%(name)s:%(lineno)-3s] [%(conn_id)s] %(message)s',
        datefmt = '%a %d %b %Y %H:%M:%S'
    )

    log = logging.getLogger(__name__)
    log.connection_id = 'master'

    vsmtpd = Vsmtpd(options, args)
    vsmtpd.load_plugins()
    try:
        vsmtpd.start()
    except KeyboardInterrupt:
        vsmtpd.stop()
