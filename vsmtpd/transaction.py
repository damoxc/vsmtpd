#
# vsmtpd/transaction.py
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

class Transaction(object):

    @property
    def connection(self):
        """
        Returns the Connection that this transaction belongs to.
        """
        return self._connection

    @property
    def body_filename(self):
        """ 
        Returns the temporary filename used to store the message contents;
        useful for virus scanners so that an additional copy doesn't need
        to be made.

        Calling `body_filename` also forces spooling to disk. A message is
        not spooled to disk if it's size is smaller than
        config['size_threshold'], default threshold is 0, the sample config
        file sets this to 10000.
        """
        pass

    @property
    def data_size(self):
        return 0

    @property
    def recipients(self):
        return self._recipients

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        self._sender = value
        return self._sender

    def __init__(self, connection):
        self._connection = connection
        self._recipients = []
        self._sender     = None

    def add_recipient(self, recipient):
        pass

    def remove_recipient(self, recipient):
        pass
