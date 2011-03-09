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

    @property
    def canonify(self):
        return (self.user, self.host)

    @property
    def notes(self):
        return self._notes

    def __init__(self, user, host=None, name=None):
        name, address = parseaddr(user)

        if '@' in address:
            self.name            = name
            self.user, self.host = address.split('@')
        else:
            self.user = user
            self.host = host
            self.name = name

        self._notes = {}
    
    def format(self):
        return str(self)

    def __str__(self):
        return formataddr((self.name, '%s@%s' % self.canonify))

    @staticmethod
    def parse(address):
        return Address(address)

        if '@' not in addr:
            raise AddressParseError("Unable to parse: '%s'" % address)
        return Address(addr, name)
