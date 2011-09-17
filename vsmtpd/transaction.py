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
from email.feedparser import FeedParser
from tempfile import NamedTemporaryFile
from vsmtpd.address import Address
from vsmtpd.util import NoteObject

class Spool(object):
    """
    Thin wrapper around either a file-object or a cStringIO object. Allows
    use of the body attribute without losing functionality by avoiding
    the class level methods of the transaction.
    """

    @property
    def body_start(self):
        return self._body_start

    @property
    def name(self):
        return self._filename

    def __init__(self):
        self._body_start = 0
        self._filename = None
        self._fp       = None
        self._parser   = None
        self._rollover = 262144 # 256kb

    def __getattr__(self, key):
        return getattr(self._fp, key)

    def end_headers(self):
        """
        Close off the parser and return the headers.
        """
        self._body_start = self._fp.tell()
        return self._parser.close()

    def flush(self):
        """
        Flushes the data held in memory to a temporary file on disk.
        """
        # Check to see if the data has been flushed already
        if self._filename:
            return

        # Create the named temporary file to write the data to
        fp = self._fp
        newfp = self._fp = NamedTemporaryFile(dir='/tmp', prefix='')
        if fp:
            newfp.write(fp.getvalue())
            newfp.seek(fp.tell(), 0)
            fp.close()

        self._filename = newfp.name

    def write(self, data):
        """
        Write data to the end of the email.

        :param data: The data to add to the end of the email
        :type data: str
        """
        if not self._fp:
            self._fp = StringIO()
            self._parser = FeedParser()

        if (self._fp.tell() + len(data)) > self._rollover:
            self.flush()

        self._fp.write(data)
        self._parser.feed(data)

class Transaction(NoteObject):
    """
    The Transaction class contains all the data relating to a single SMTP
    session. This data includes the message sender, recipients, message
    headers and body.
    """

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
        if not self._body:
            self._body = Spool()
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
        if not self.body.name:
            self.flush()

        return self.body.name

    @property
    def data_size(self):
        """
        Get the current size of the email. Note that this is not the size
        of the message that will be queued, it is the size of what the
        client sent after the "DATA" command.
        """
        return self._body.tell() if self._body else 0

    @property
    def headers(self):
        """
        Create an email.message.Message object that contains the contents
        of the messages headers.
        """
        return self._headers

    @property
    def recipients(self):
        """
        This returns the list of the current recipients for the mail
        envelope.
        """
        return self._recipients

    @property
    def sender(self):
        """
        Get or set the sender of the email to be used in the mail envelope.
        """
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
        self._headers    = None
        self._header_size = 0

    def add_recipient(self, recipient):
        """
        Add a recipient to the mail envelope of this message.

        :param recipient: The address to add
        :type recipient: str or Address
        """
        if not isinstance(recipient, Address):
            recipient = Address(recipient)
        self._recipients.append(recipient)

    def close(self):
        """
        Dispose all the resources that this transaction has opened.
        """
        if self._body:
            self._body.close()

    def end_headers(self):
        """
        Mark the end of the messages headers and the beginning of the
        body.
        """
        self._headers = self.body.end_headers()

    def flush(self):
        """
        Flushes the data held in memory to a temporary file on disk.
        """
        self.body.flush()

    def remove_recipient(self, recipient):
        """
        Remove a recipient from the mail envelope of this message.

        :param recipient: The address to remove
        :type recipient: str or Address
        """
        if not isinstance(recipient, Address):
            recipient = Address(recipient)
        self._recipients.remove(recipient)
