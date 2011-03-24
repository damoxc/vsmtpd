#
# vsmtpd/tests/test_commands.py
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

from vsmtpd.commands import parse
from vsmtpd.tests.common import TestCase

class CommandsTestCase(TestCase):

    def test_helo_parse(self):
        helo = 'local.localdomain'
        self.assertEqual(parse('helo', helo), ['local.localdomain'])

    def test_ehlo_parse(self):
        ehlo = 'local.localdomain'
        self.assertEqual(parse('ehlo', ehlo), ['local.localdomain'])

    def test_mail_parse(self):
        mail = 'FROM:<john.smith@example.com>'
        self.assertEqual(parse('mail', mail), ('<john.smith@example.com>', []))

    def test_mail_with_args_parse(self):
        mail = 'FROM:<john.smith@example.com> SIZE=512'
        self.assertEqual(parse('mail', mail), ('<john.smith@example.com>', ['SIZE=512']))

    def test_rcpt_parse(self):
        rcpt = 'TO:<john.smith@example.com>'
        self.assertEqual(parse('rcpt', rcpt), ('<john.smith@example.com>', []))

    def test_rcpt_with_args_parse(self):
        rcpt = 'TO:<john.smith@example.com> MAX=53'
        self.assertEqual(parse('rcpt', rcpt), ('<john.smith@example.com>', ['MAX=53']))
