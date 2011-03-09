#
# vsmtpd/address.py
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

from email.utils import formataddr, parseaddr
from vsmtpd.error import AddressParseError

class Address(object):

    def __init__(self, address, name=None):
        self.address         = address
        self.name            = name
        self.user, self.host = address.split('@')

    def __str__(self):
        return formataddr((self.name, self.address))

    @staticmethod
    def parse(address):
        name, addr = parseaddr(address)
        if '@' not in addr:
            raise AddressParseError("Unable to parse: '%s'" % address)
        return Address(addr, name)
