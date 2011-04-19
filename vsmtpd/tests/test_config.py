#
# vsmtpd/tests/test_config.py
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

from vsmtpd.config import (
    _dict_to_defaults,
    load_config,
    load_simple_config,
    ConfigWrapper
)

from vsmtpd.util import OrderedDict
from vsmtpd.tests.common import TestCase

CONFIG = """[test_section]
test_var2 = 
test_var1 = 1

"""

DNSBL = [
    'b.barracudacentral.org',
    'spamsources.fabel.dk',
    'sbl-xbl.spamhaus.org',
    'bl.spamcop.net',
    'rbl.mail-abuse.org'
]

class ConfigWrapperTestCase(TestCase):

    def test_config_wrapper(self):
        path = os.path.join(os.path.dirname(__file__), 'test_config.cfg')
        config = ConfigWrapper(load_config(path), 'vsmtpd')
        self.assertEqual(config.get('helo_host'), 'smtp.example.com')
        self.assertEqual(config.getint('port'), 25)
        self.assertEqual(config.getfloat('float'), 3.123)
        self.assertEqual(config.getboolean('ssl'), True)
        self.assertTrue(config.has_option('backlog'))

        items = [
            ('port', '25'),
            ('workers', '4'),
            ('backlog', '250'),
            ('helo_host', 'smtp.example.com'),
            ('ssl', 'true'),
            ('float', '3.123')
        ]
        options = [i[0] for i in items]
        self.assertEqual(config.items(), items)
        self.assertEqual(config.options(), options)
        self.assertTrue('port' in config)

        config.set('backlog', '150')
        self.assertEqual(config.getint('backlog'), 150)

class ConfigTestCase(TestCase):

    def test_dict_to_defaults(self):
        self.assertEqual(_dict_to_defaults({'test_section': {
            'test_var1': 1,
            'test_var2': None
        }}).getvalue(), CONFIG)

    def test_load_simple_config(self):
        path = os.path.join(os.path.dirname(__file__), 'rbldns')
        self.assertEqual(list(load_simple_config(path)), DNSBL)
