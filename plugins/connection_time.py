#
# connection_time.py
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
The **connection_time** plugin records the time of a connection between the
first and the last possible hook in vsmtpd (*pre-connection* and
*post-connection*) and writes an entry to the log.

One optional argument: the name of the log level (e.g. INFO, DEBUG, ...)
the message should be logged with. Default to INFO.
"""

import time
import logging

from vsmtpd.hooks import hook
from vsmtpd.plugins.plugin import PluginBase

log = logging.getLogger(__name__)

class Plugin(PluginBase):

    def __init__(self, config):
        self.level = 'INFO'
        #self.level = config.get('level') or 'INFO'

    @hook
    def pre_connection(self, connection):
        connection.notes['connection_start'] = time.time()

    @hook
    def post_connection(self, connection):
        if 'connection_start' not in connection.notes:
            return
        remote = connection.remote_ip
        elapsed = time.time() - connection.notes['connection_start']
        log.info('Connection time from %s: %.3f sec.', remote, elapsed)

