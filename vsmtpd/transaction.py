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

from cStringIO import StringIO
from tempfile import NamedTemporaryFile
from vsmtpd.address import Address

class Transaction(object):

    @property
    def connection(self):
        """
        Returns the Connection that this transaction belongs to.
        """
        return self._connection

    @property
    def body(self):
        """
        Returns the file-like object that contains the body of the email.
        This may be an actual file handle or simply a file-like object in
        memory depending on the email size of if body_filename has not
        been accessed.
        """
        return self._body

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
        # We have to write the email to disk now into our spool directory
        # and update the body variable.
        if not self._body_fn and self._body:
            self.flush()

        return self._body_fn

    @property
    def data_size(self):
        return 0

    @property
    def notes(self):
        return self._nodes = {}

    @property
    def recipients(self):
        """
        This returns the list of the current recipients for the mail
        envelope.
        """
        return self._recipients

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        if not isinstance(value, Address):
            value = Address(value)
        self._sender = value
        return self._sender

    def __init__(self, connection):
        self._connection = connection
        self._recipients = []
        self._sender     = None
        self._body       = None
        self._body_fn    = None
        self._notes      = {}

    def add_recipient(self, recipient):
        if not isinstance(recipient, Address):
            recipient = Address(recipient)
        self._recipients.append(recipient)

    def body_write(self, data):
        """
        Write data to the end of the email.

        :param data: The data to add to the end of the email
        :type data: str
        """
        if not self._body:
            self._body = StringIO()
        self._body.write(data)

    def remove_recipient(self, recipient):
        if not isinstance(recipient, Address):
            recipient = Address(recipient)
        self._recipients.remove(recipient)

    def flush(self):
        """
        Flushes the data held in memory to a temporary file on disk.
        """
        # Check to see if the data has been flushed already
        if self._body_fn:
            return

        # Create the named temporary file to write the data to
        fh = NamedTemporaryFile(dir='/tmp', prefix='')
        fh.write(self._body.getvalue())
        self._body.close()
        self._body = fh
        self._body_fn = fh.name
