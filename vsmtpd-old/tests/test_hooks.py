#
# vsmtpd/tests/test_hooks.py
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

from vsmtpd.error import HookNotFoundError
from vsmtpd.hooks import hook
from vsmtpd.hooks import HookManager
from vsmtpd.tests.common import TestCase

class SamplePlugin(object):

    @hook
    def rcpt(self, foo):
        pass

    @hook('rcpt')
    def foo(self, bar):
        pass

    @hook('connect', 'rcpt')
    def bar(self, *args):
        pass

class HookDecoratorTestCase(TestCase):

    @hook('rcpt')
    def foo(self, bar):
        pass

    def test_hook_decorator(self):
        self.assertTrue(SamplePlugin.rcpt._is_hook)
        self.assertEqual(SamplePlugin.rcpt._hook_names, ('rcpt',))

    def test_hook_decorator_with_name(self):
        self.assertTrue(SamplePlugin.foo._is_hook)
        self.assertEqual(SamplePlugin.foo._hook_names, ('rcpt',))

    def test_hook_decorator_with_multiple_names(self):
        self.assertTrue(SamplePlugin.bar._is_hook)
        self.assertEqual(SamplePlugin.bar._hook_names, ('connect', 'rcpt'))

    def test_hook_decorator_no_arguments(self):
        self.assertRaises(TypeError, hook)

class HookManagerTestCase(TestCase):

    def setUp(self):
        self.manager = HookManager()

    def test_register_object(self):
        self.manager.register_object(SamplePlugin())
        self.assertEqual(len(self.manager.hooks['rcpt']), 3)

    def test_register_missing_hook(self):
        self.assertRaises(HookNotFoundError, self.manager.register_hook,
                          'foo', None)

    def test_deregister_hook(self):
        plugin = SamplePlugin()
        self.manager.register_object(plugin)
        self.manager.deregister_hook('rcpt', plugin.foo)
        self.assertEqual(len(self.manager.hooks['rcpt']), 2)

    def test_deregister_missing_hook(self):
        self.assertRaises(HookNotFoundError, self.manager.deregister_hook,
                          'foo', None)
