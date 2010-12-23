#
# vsmtpd/plugins/core/quit_fortune.py
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

from twisted.internet import utils

from vsmtpd.hooks import hook
from vsmtpd.plugins.plugin import Plugin

FORTUNE = '/usr/bin/fortune'

class QuitFortune(Plugin):

    @hook
    def quit(self, connection):
        # Skip if the other party is talking EHLO, they probably won't 
        # appreciate the gag.
        if connection.hello == 'ehlo':
            return self.declined()

        # Skip if fortune isn't installed on the system
        if not os.path.exists(FORTUNE):
            return self.declined()

        return utils.getProcessOutput(FORTUNE, ('-s',)
            ).addCallback(self.on_response, connection)

    def on_response(self, response, connection):
        connection.sendCode(221, response.strip())
        return self.done()
