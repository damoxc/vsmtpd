#
# vsmtpd/tests/test_plugin_manager.py
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

from vsmtpd.error import PluginNotFoundError
from vsmtpd.plugins.manager import PluginManager
from vsmtpd.tests.common import TestCase

class PluginManagerTestCase(TestCase):

    def setUp(self):
        plugins = os.path.join(os.path.dirname(__file__), 'pluginsdir')
        self.manager = PluginManager([plugins])

    def test_simple_valid_plugin(self):
        plugin_cls = self.manager.load('simple_valid_plugin')

    def test_simple_invalid_plugin(self):
        self.assertRaises(PluginNotFoundError, self.manager.load,
            'simple_invalid_plugin')

    def test_subdirectory_valid_plugin(self):
        self.manager.load('queue.simple_valid_plugin')

    def test_subdirectory_invalid_plugin(self):
        self.assertRaises(PluginNotFoundError, self.manager.load,
            'queue.simple_invalid_plugin')

    def test_missing_plugin(self):
        self.assertRaises(PluginNotFoundError, self.manager.load,
            'missing_pugin')

    def test_missing_subdirectory_plugin(self):
        self.assertRaises(PluginNotFoundError, self.manager.load,
            'queue.missing_pugin')
