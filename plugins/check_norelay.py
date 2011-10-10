#
# check_norelay.py
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

"""
This plugin checks the norelayclients config file to see if relaying
is denied.

This allows specific clients, such as the gateway, to be denied relaying,
event though they would be allowed relaying by the relayclients file.

Each line is:
- a full IP address
- partial IP address for matching whole networks
  e.g. 192.168.42

This plugin does not have a more_norelayclients map equivalent of the
more_relayclients map of the check_relay plugin.

Based on the check_norelay plugin from qpsmtpd.
Copyright 2005 Gordon Rowell <gordonr@gormand.com.au>
"""

import logging

from vsmtpd.hooks import hook
from vsmtpd.plugins.plugin import PluginBase

log = logging.getLogger(__name__)

class Plugin(PluginBase):

    @hook
    def connect(self, connection):
        no_relay_clients = self.simple_config('norelayclients')
        no_relay_clients = dict(((k, True) for k in no_relay_clients))
        client_ip = connection.remote_ip
        while client_ip:
            if no_relay_clients.get(client_ip, False):
                connection.relay_client = False
                log.info('%s denied relaying', client_ip)
                break
            client_ip = ''.join(client_ip.rpartition('.')[0:1])
