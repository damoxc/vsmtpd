#
# vsmtpd/tests/test_plugin.py
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

from vsmtpd.error import (
    DenyError,
    DenySoftError,
    DenyDisconnectError,
    DenySoftDisconnectError,
    DoneError,
    OkayError
)
from vsmtpd.plugins.plugin import PluginBase
from vsmtpd.tests.common import TestCase

class PluginBaseTestCase(TestCase):

    def setUp(self):
        self.plugin = PluginBase()

    def test_plugin_decline(self):
        self.assertEquals(self.plugin.declined(), None)

    def test_plugin_deny(self):
        self.assertRaises(DenyError, self.plugin.deny)

    def test_plugin_deny_disconnect(self):
        self.assertRaises(DenyDisconnectError, self.plugin.deny, disconnect=True)

    def test_plugin_denysoft(self):
        self.assertRaises(DenySoftError, self.plugin.deny_soft)

    def test_plugin_denysoft_disconnect(self):
        self.assertRaises(DenySoftDisconnectError, self.plugin.deny_soft, disconnect=True)

    def test_plugin_done(self):
        self.assertRaises(DoneError, self.plugin.done)

    def test_plugin_ok(self):
        self.assertRaises(OkayError, self.plugin.ok)

    def test_plugin_vsmtpd(self):
        self.assertEqual(self.plugin.vsmtpd, None)
