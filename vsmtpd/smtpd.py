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

import os
import sys
import logging
import pkg_resources

from twisted.internet import reactor
from twisted.mail.smtp import ESMTP, SMTPFactory as _SMTPFactory

from vsmtpd.common import *
from vsmtpd.config import load_config
from vsmtpd.error import PluginNotFoundError
from vsmtpd.hooks import HookManager

log = logging.getLogger(__name__)

class SMTP(ESMTP):
    """
    Handles the basic ESMTP communication, firing off the hooks to
    allow plugins to extend any point of the smtp communication.
    """

    def disconnect(self, code, message=''):
        """
        Handles performing DENY(|SOFT)_DISCONNECT, sending the appropriate
        response and disconnecting the client.

        :param code: The response code to send.
        :type code: int
        :keyword message: What to output after disconnecting
        :type message: str
        """

        # Set a default message if there isn't one
        if not message:
            message = 'Good bye!'

        # Call any plugins that hook into a disconnect
        self.dispatch('disconnect')

        # Send the client the code and message
        self.sendCode(code, message)

        # Disconnect the client
        self.transport.loseConnection()

    def dispatch(self, hook_name, *args):
        """
        Proxy method to dispatch hooks and convert the response
        into a standard form.

        :param hook_name: The name of the hook
        :type hook_name: str
        """
        return self.factory.hooks.dispatch(self, hook_name, *args)

    def makeConnection(self, transport):
        self.transport = transport
        self.connection = Connection(self)
        self.transaction = None

        # Execute the hooks
        return self.dispatch('pre_connection', self.connection
            ).addCallback(self._cbPreConnection, transport
            ).addErrback(self._ebPreConnection)

    def _cbPreConnection(self, (result, message), transport):
        # No plugin opted to take charge here, revert to default action
        if not result or result == DECLINED:
            ESMTP.makeConnection(self, transport)

    def _ebPreConnection(self, error):
        self.disconnect(451)
    
    def connectionMade(self):
        return self.dispatch('connect', self.connection
            ).addCallback(self._cbConnect
            ).addErrback(self._ebConnect)

    def _cbConnect(self, (result, message)):
        if not result or result in (DECLINED, OK):
            return ESMTP.connectionMade(self)

    def _ebConnect(self, error):
        self.disconnect(451)

    def connectionLost(self, reason):
        self.dispatch('post_connection', self.connection)
        return ESMTP.connectionLost(self, reason)

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
        return self.dispatch('helo', self.connection
            ).addCallback(self._cbHelo, rest)

    def _cbHelo(self, (result, message), rest):
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
        return self.dispatch('quit', self.connection
            ).addCallback(self._cbQuit, rest)

    def _cbQuit(self, (result, message), rest):
        if not result or result in (DECLINED, OK):
            return ESMTP.do_QUIT(self, rest)
        else:
            self.transport.loseConnection()

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
        self.config = load_config('vsmtpd.cfg')
        self.factory = SMTPFactory()
        self.factory.smtpd = self
        self.factory.hooks = HookManager()
        self.factory.max_size = self.config.getint('vsmtpd', 'max_size')
        self.interfaces = None
        self.port = self.config.getint('vsmtpd', 'port')
        self.plugins = {}
        self.enabled_plugins = {}
        self.scan_plugins()

    def enable_plugin(self, name, *args):
        """
        Enable a plugin providing the specified arguments.

        :param name: The plugin name to enable
        :type name: str
        """

        # First check to see if we have a plugin by that name
        if name not in self.plugins:
            raise PluginNotFoundError(name)

        try:
            # Get the plugin class
            class_ = self.plugins[name].load()

            # Try to instantiate the plugin
            instance = class_(*args)

            # Scan the plugin for hooks
            self.factory.hooks.scan_plugin(instance)

            # Store the plugin for later just incase
            self.enabled_plugins[name] = instance
        except Exception as e:
            log.exception(e)
            log.fatal("Unable to create plugin '%s' using %r", name,
                args)
            sys.exit(1)
        else:
            log.info("Plugin '%s' enabled", name)

    def scan_plugins(self):
        """
        Scans the main plugins directory for any plugins available, storing
        them so they can easily be enabled.
        """
        entry_point = 'vsmtpd.plugins'

        plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        pkg_resources.working_set.add_entry(plugin_dir)
        self.pkg_env = pkg_resources.Environment([plugin_dir])

        self.plugins = {}
        for pkg_name in self.pkg_env:
            egg = self.pkg_env[pkg_name][0]
            egg.activate()
            for name in egg.get_entry_map(entry_point):
                entry_info = egg.get_entry_info(entry_point, name)
                self.plugins[entry_info.name] = entry_info

    def start(self):
        """
        Starts the server and enables all the plugins specified in the
        configuration file.
        """
        for (plugin, empty) in self.config.items('plugins'):
            self.enable_plugin(plugin)

        self.port = reactor.listenTCP(self.port, self.factory)
