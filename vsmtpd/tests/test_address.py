#
# vsmtpd/tests/test_address.py
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

from vsmtpd.address import Address
from vsmtpd.tests.common import TestCase

class AddressTestCase(TestCase):
    
    def test_simple_parse(self):
        address = Address('test@example.com')
        self.assertEqual(address.user, 'test')
        self.assertEqual(address.host, 'example.com')

    def test_parse(self):
        address = Address('<test@example.com>')
        self.assertEqual(address.user, 'test')
        self.assertEqual(address.host, 'example.com')

    def test_parse_with_name(self):
        address = Address('John Smith <test@example.com>')
        self.assertEqual(address.user, 'test')
        self.assertEqual(address.host, 'example.com')
        self.assertEqual(address.name, 'John Smith')
