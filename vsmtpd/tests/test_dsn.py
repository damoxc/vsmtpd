#
# vsmtpd/tests/test_dsn.py
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

from vsmtpd  import dsn
from vsmtpd.tests.common import TestCase

class DSNTestCase(TestCase):

    def test_status_method(self):
        self.assertEqual(dsn._status(dsn.DENY), 5)
        self.assertEqual(dsn._status(dsn.DENY_DISCONNECT), 5)
        self.assertEqual(dsn._status(dsn.DENYSOFT), 4)
        self.assertEqual(dsn._status(dsn.DENYSOFT_DISCONNECT), 4)
        self.assertEqual(dsn._status(dsn.OK), 2)
        self.assertEqual(dsn._status(dsn.DONE), 2)
        self.assertEqual(dsn._status(dsn.DECLINED), 4)
        self.assertEqual(dsn._status(dsn.YIELD), 4)

    def test_dsn_method(self):
        self.assertEqual(dsn._dsn(dsn.DENYSOFT, None, dsn.DENY, 1, 2),
                         (902, 'Bad destination system address. (#4.1.2)'))
        self.assertEqual(dsn._dsn(dsn.DENY, None, dsn.DENYSOFT, 4, 3),
                         (901, 'Directory server failure. (#5.4.3)'))

    def test_dsn_codes(self):
       self.assertEqual(dsn.unspecified(),
                        (902, 'Other or Undefined Status (#4.0.0)'))
       self.assertEqual(dsn.addr_unspecified(),
                        (902, 'Other address status. (#4.1.0)'))
       self.assertEqual(dsn.no_such_user(),
                        (902, 'No such user (#4.1.0)'))
       self.assertEqual(dsn.addr_bad_dest_mbox(),
                        (901, 'Bad destination mailbox address. (#5.1.1)'))
       self.assertEqual(dsn.addr_bad_dest_system(),
                        (901, 'Bad destination system address. (#5.1.2)'))
       self.assertEqual(dsn.addr_bad_dest_syntax(),
                        (901, 'Bad destination mailbox address syntax. (#5.1.3)'))
       self.assertEqual(dsn.addr_bad_dest_ambigous(),
                        (902, 'Destination mailbox address ambiguous. (#4.1.4)'))
       self.assertEqual(dsn.addr_rcpt_ok(),
                        (900, 'Destination address valid. (#2.1.5)'))
       self.assertEqual(dsn.addr_mbox_moved(),
                        (901, 'Destination mailbox has moved, No forwarding address. (#5.1.6)'))
       self.assertEqual(dsn.addr_bad_from_syntax(),
                        (901, "Bad sender's mailbox address syntax. (#5.1.7)"))
       self.assertEqual(dsn.addr_bad_from_system(),
                        (901, "Bad sender's system address. (#5.1.8)"))
       self.assertEqual(dsn.mbox_unspecified(),
                        (902, 'Other or undefined mailbox status. (#4.2.0)'))
       self.assertEqual(dsn.mbox_disabled(),
                        (901, 'Mailbox disabled, not accepting messages. (#5.2.1)'))
       self.assertEqual(dsn.mbox_full(),
                        (902, 'Mailbox full. (#4.2.2)'))
       self.assertEqual(dsn.mbox_msg_too_long(),
                        (901, 'Message length exceeds administrative limit. (#5.2.3)'))
       self.assertEqual(dsn.mbox_list_expansion_problem(),
                        (902, 'Mailing list expansion problem. (#4.2.4)'))
       self.assertEqual(dsn.sys_unspecified(),
                        (902, 'Other or undefined mail system status. (#4.3.0)'))
       self.assertEqual(dsn.sys_disk_full(),
                        (902, 'Mail system full. (#4.3.1)'))
       self.assertEqual(dsn.sys_not_accepting_mail(),
                        (902, 'System not accepting network messages. (#4.3.2)'))
       self.assertEqual(dsn.sys_not_supported(),
                        (902, 'System not capable of selected features. (#4.3.3)'))
       self.assertEqual(dsn.sys_msg_too_big(),
                        (901, 'Message too big for system. (#5.3.4)'))
       self.assertEqual(dsn.net_unspecified(),
                        (902, 'Other or undefined network or routing status. (#4.4.0)'))
       self.assertEqual(dsn.temp_resolver_failed(),
                        (902, 'Temporary address resolution failure (#4.4.3)'))
       self.assertEqual(dsn.net_directory_server_failed(),
                        (902, 'Directory server failure. (#4.4.3)'))
       self.assertEqual(dsn.net_system_congested(),
                        (902, 'Mail system congestion. (#4.4.5)'))
       self.assertEqual(dsn.net_routing_loop(),
                        (901, 'Routing loop detected. (#5.4.6)'))
       self.assertEqual(dsn.too_many_hops(),
                        (901, 'Too many hops (#5.4.6)'))
       self.assertEqual(dsn.proto_unspecified(),
                        (902, 'Other or undefined protocol status. (#4.5.0)'))
       self.assertEqual(dsn.proto_invalid_command(),
                        (901, 'Invalid command. (#5.5.1)'))
       self.assertEqual(dsn.proto_syntax_error(),
                        (901, 'Syntax error. (#5.5.2)'))
       self.assertEqual(dsn.proto_rcpt_list_too_long(),
                        (902, 'Too many recipients. (#4.5.3)'))
       self.assertEqual(dsn.too_many_rcpts(),
                        (902, 'Too many recipients. (#4.5.3)'))
       self.assertEqual(dsn.proto_invalid_cmd_args(),
                        (901, 'Invalid command arguments. (#5.5.4)'))
       self.assertEqual(dsn.proto_wrong_version(),
                        (902, 'Wrong protocol version. (#4.5.5)'))
       self.assertEqual(dsn.media_unspecified(),
                        (902, 'Other or undefined media error. (#4.6.0)'))
       self.assertEqual(dsn.media_unsupported(),
                        (901, 'Media not supported. (#5.6.1)'))
       self.assertEqual(dsn.media_conv_prohibited(),
                        (901, 'Conversion required and prohibited. (#5.6.2)'))
       self.assertEqual(dsn.media_conv_unsupported(),
                        (902, 'Conversion required but not supported. (#4.6.3)'))
       self.assertEqual(dsn.media_conv_lossy(),
                        (902, 'Conversion with loss performed. (#4.6.4)'))
       self.assertEqual(dsn.sec_unspecified(),
                        (902, 'Other or undefined security status. (#4.7.0)'))
       self.assertEqual(dsn.sec_sender_unauthorized(),
                        (901, 'Delivery not authorized, message refused. (#5.7.1)'))
       self.assertEqual(dsn.bad_sender_ip(),
                        (901, "Bad sender's IP (#5.7.1)"))
       self.assertEqual(dsn.relaying_denied(),
                        (901, 'Relaying denied (#5.7.1)'))
       self.assertEqual(dsn.sec_list_dest_prohibited(),
                        (901, 'Mailing list expansion prohibited. (#5.7.2)'))
       self.assertEqual(dsn.sec_conv_failed(),
                        (901, 'Security conversion required but not possible. (#5.7.3)'))
       self.assertEqual(dsn.sec_feature_unsupported(),
                        (901, 'Security features not supported. (#5.7.4)'))
       self.assertEqual(dsn.sec_crypto_failure(),
                        (901, 'Cryptographic failure. (#5.7.5)'))
       self.assertEqual(dsn.sec_crypto_algorithm_unsupported(),
                        (902, 'Cryptographic algorithm not supported. (#4.7.6)'))
       self.assertEqual(dsn.sec_msg_integrity_failure(),
                        (901, 'Message integrity failure. (#5.7.7)'))
