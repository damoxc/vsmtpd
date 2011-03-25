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

from email.utils import formataddr
from email.utils import parseaddr

from vsmtpd.error import AddressParseError
from vsmtpd.util import NoteObject

class Address(NoteObject):

    @property
    def canonify(self):
        return (self.user, self.host)

    def __init__(self, user, host=None, name=None):
        name, address = parseaddr(user)

        if '@' in address:
            self.name            = name
            self.user, self.host = address.split('@')
        else:
            self.user = user
            self.host = host
            self.name = name
    
    def format(self):
        return str(self)

    def __cmp__(self, other):
        test = cmp(self.user, other.user)
        if test:
            return test

        test = cmp(self.host, other.host)
        if test:
            return test

        return cmp(self.name, other.name)

    def __str__(self):
        return formataddr((self.name, '%s@%s' % self.canonify))

    @staticmethod
    def parse(address):
        return Address(address)

        if '@' not in addr:
            raise AddressParseError("Unable to parse: '%s'" % address)
        return Address(addr, name)
