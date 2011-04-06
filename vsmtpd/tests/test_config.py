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
    load_simple_config
)

from vsmtpd.util import OrderedDict
from vsmtpd.tests.common import TestCase

CONFIG = """[test_section]
test_var2 = 2
test_var1 = 1

"""

DNSBL = [
    'b.barracudacentral.org',
    'spamsources.fabel.dk',
    'sbl-xbl.spamhaus.org',
    'bl.spamcop.net',
    'rbl.mail-abuse.org'
]

class ConfigTestCase(TestCase):

    def test_dict_to_defaults(self):
        self.assertEqual(_dict_to_defaults({'test_section': {
            'test_var1': 1, 
            'test_var2': 2
        }}).getvalue(), CONFIG)

    def test_load_simple_config(self):
        path = os.path.join(os.path.dirname(__file__), 'rbldns')
        self.assertEqual(list(load_simple_config(path)), DNSBL)
