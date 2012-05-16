#
# vsmtpd/logging_setup.py
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

import gevent
import logging

connection_ids = {}

class ConnectionLogRecord(logging.LogRecord):
    """
    Custom LogRecord class that sets the current connection id so it can
    be output in the log to allow for easy sorting of log entries in a
    massively concurrent environment.
    """

    def __init__(self, name, level, fn, lno, msg, args, exc_info, func,
                 connection_id):
        logging.LogRecord.__init__(self, name, level, fn, lno, msg, args,
            exc_info, func)
        self.conn_id = connection_id

class Logger(logging.Logger, object):
    """
    Custom Logger to support setting the connection id on a per greenlet
    basis.
    """

    @property
    def connection_id(self):
        return connection_ids.get(gevent.getcurrent(), '')

    @connection_id.setter
    def connection_id(self, value):
        connection_ids[gevent.getcurrent()] = value

    @connection_id.deleter
    def connection_id(self):
        del connection_ids[gevent.getcurrent()]

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info,
                   func=None, extra=None):
        lr = ConnectionLogRecord(name, level, fn, lno, msg, args, exc_info,
            func, self.connection_id)

        if not extra:
            return lr

        for key in extra:
            if (key in ['message', 'asctime']) or (key in lr.__dict__):
                raise KeyError('Attempt to overwrite %r in LogRecord' % key)
            lr.__dict__[key] = extra[key]

        return lr

logging.setLoggerClass(Logger)
