#
# count_unrecognized_commands.py
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

from vsmtpd.error import DenyDisconnectError
from vsmtpd.hooks import hook
from vsmtpd.plugins.plugin import PluginBase

log = logging.getLogger(__name__)

class Plugin(PluginBase):

    unrec_cmd_max = 4

    @hook
    def unknown(self, transaction, command, *parts):
        connection = transaction.connection

        log.info("Unrecognized command '%s'", command)

        bad_cmd_count = connection.notes.setdefault('unrec_cmd_count', 0) + 1
        if bad_cmd_count >= self.unrec_cmd_max:
            log.info('Closing connection. Too many unrecognized commands')
            raise DenyDisconnectError('Closing connection. %d unrecognized commands. Perhaps you should read RFC 2821?' % bad_cmd_count)
