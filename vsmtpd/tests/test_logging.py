#
# vsmtpd/tests/test_logging.py
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

from vsmtpd.logging_setup import ConnectionLogRecord
from vsmtpd.logging_setup import Logger
from vsmtpd.tests.common import TestCase

class LoggingTestCase(TestCase):

    def test_logger_connection_id(self):
        log = logging.getLogger(__name__)
        log.connection_id = 'test'
        self.assertEqual(log.connection_id, 'test')

        del log.connection_id
        self.assertEqual(log.connection_id, '')

    def test_logger_make_record(self):
        log = logging.getLogger(__name__)
        log.connection_id = 'test'
        log_record = log.makeRecord(__name__, logging.INFO, 
                                    'test_logging.py', 43, 
                                    'This is a test', None, None,
                                    'test_logger_make_record')

        self.assertEqual(log_record.conn_id, 'test')
        self.assertEqual(log_record.name, __name__)
        self.assertEqual(log_record.levelname, 'INFO')
        self.assertEqual(log_record.filename, 'test_logging.py')
        self.assertEqual(log_record.funcName, 'test_logger_make_record')
        self.assertEqual(log_record.lineno, 43)
        self.assertEqual(log_record.msg, 'This is a test')
        self.assertEqual(log_record.args, None)
        self.assertEqual(log_record.exc_info, None)
