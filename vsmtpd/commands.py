#
# vsmtpd/commands.py
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

import re
import logging

from vsmtpd.error import DenyError

log = logging.getLogger(__name__)

# Character classes for parsing addresses
atom = r"[-A-Za-z0-9!\#$%&'*+/=?^_`{|}~]"
# A string of quoted strings, backslash-escaped character or
# atom characters + '@.,:'
qstring = r'("[^"]*"|\\.|' + atom + r'|[@.,:])+'

mail_re = re.compile(r'''\s*FROM:\s*(?P<path><> # Empty <>
                     |<''' + qstring + r'''> # <addr>
                     |''' + qstring + r''' # addr
                     )\s*(\s(?P<opts>.*))? # Optional WS + ESMTP options
                     $''', re.I | re.X)
rcpt_re = re.compile(r'\s*TO:\s*(?P<path><' + qstring + r'''> # <addr>
                     |''' + qstring + r''' # addr
                     )\s*(\s(?P<opts>.*))? # Optional WS + ESMTP options
                     $''', re.I | re.X)

def parse(command, line):
    if not line:
        return None

    if command in parsers:
        return parsers[command](command, line)

def parse_rcpt(command, line):
    m = rcpt_re.match(line)
    if not m:
        raise DenyError('Syntax error in command')
    return (m.group('path'), m.group('opts').split() if 
        m.group('opts') else [])

def parse_mail(command, line):
    m = mail_re.match(line)
    if not m:
        raise DenyError('Syntax error in command')
    return (m.group('path'), m.group('opts').split() if 
        m.group('opts') else [])

parsers = {
    'rcpt': parse_rcpt,
    'mail': parse_mail
}
