#
# vsmtpd/tests/test_daemon.py
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
import logging

from vsmtpd.tests.common import TestCase, create_daemon

class DaemonTestCase(TestCase):

    def test_daemon_creation(self):
        vsmtpd = create_daemon(port=2500)
        self.assertEqual(vsmtpd.options.port, 2500)
        self.assertNotEqual(vsmtpd.hook_manager, None)
        self.assertNotEqual(vsmtpd.plugin_manager, None)

    def test_daemon_load_plugins(self):
        vsmtpd = create_daemon(port=2500)
        vsmtpd.plugin_manager.path.append(os.path.join(os.path.dirname(__file__), 'pluginsdir'))
        vsmtpd._config.add_section('plugin:simple_valid_plugin')
        vsmtpd._config.add_section('plugin:queue.simple_valid_plugin')
        vsmtpd.load_plugins()
