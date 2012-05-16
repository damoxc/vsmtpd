#
# vsmtpd/tests/plugins/test_connection_time.py
#
# Copyright (C) 2011 Damien Churchill <damoxc@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.    If not, write to:
#   The Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor
#   Boston, MA    02110-1301, USA.
#

import time

from vsmtpd.tests.common import PluginTestCase, create_connection

class ConnectionTimeTestCase(PluginTestCase):

    plugin_name = 'connection_time'

    def test_short_connection(self):
        plugin = self.plugin(None)
        connection = create_connection()
        plugin.pre_connection(connection)
        time.sleep(0.1)
        plugin.post_connection(connection)
