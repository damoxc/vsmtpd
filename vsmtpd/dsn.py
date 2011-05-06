#
# vsmtpd/dsn.py
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

import sys

OK                  = 900
DENY                = 901
DENYSOFT            = 902
DENY_DISCONNECT     = 903
DENYSOFT_DISCONNECT = 904
DECLINED            = 909
DONE                = 910
YIELD               = 911

RFC1893 = (
    (
        "Other or Undefined Status",                              # x.0.x
    ),
    (
        "Other address status.",                                  # x.1.0
        "Bad destination mailbox address.",                       # x.1.1
        "Bad destination system address.",                        # x.1.2
        "Bad destination mailbox address syntax.",                # x.1.3
        "Destination mailbox address ambiguous.",                 # x.1.4
        "Destination address valid.",                             # x.1.5
        "Destination mailbox has moved, No forwarding address.",  # x.1.6
        "Bad sender's mailbox address syntax.",                   # x.1.7
        "Bad sender's system address.",                           # x.1.8
    ),
    (
        "Other or undefined mailbox status.",                     # x.2.0
        "Mailbox disabled, not accepting messages.",              # x.2.1
        "Mailbox full.",                                          # x.2.2
        "Message length exceeds administrative limit.",           # x.2.3
        "Mailing list expansion problem.",                        # x.2.4
    ),
    (
        "Other or undefined mail system status.",                 # x.3.0
        "Mail system full.",                                      # x.3.1
        "System not accepting network messages.",                 # x.3.2
        "System not capable of selected features.",               # x.3.3
        "Message too big for system.",                            # x.3.4
        "System incorrectly configured.",                         # x.3.5
    ),
    (
        "Other or undefined network or routing status.",          # x.4.0
        "No answer from host.",                                   # x.4.1
        "Bad connection.",                                        # x.4.2
        "Directory server failure.",                              # x.4.3
        "Unable to route.",                                       # x.4.4
        "Mail system congestion.",                                # x.4.5
        "Routing loop detected.",                                 # x.4.6
        "Delivery time expired.",                                 # x.4.7
    ),
    (
        "Other or undefined protocol status.",                    # x.5.0
        "Invalid command.",                                       # x.5.1
        "Syntax error.",                                          # x.5.2
        "Too many recipients.",                                   # x.5.3
        "Invalid command arguments.",                             # x.5.4
        "Wrong protocol version.",                                # x.5.5
    ),
    (
        "Other or undefined media error.",                        # x.6.0
        "Media not supported.",                                   # x.6.1
        "Conversion required and prohibited.",                    # x.6.2
        "Conversion required but not supported.",                 # x.6.3
        "Conversion with loss performed.",                        # x.6.4
        "Conversion Failed.",                                     # x.6.5
    ),
    (
        "Other or undefined security status.",                    # x.7.0
        "Delivery not authorized, message refused.",              # x.7.1
        "Mailing list expansion prohibited.",                     # x.7.2
        "Security conversion required but not possible.",         # x.7.3
        "Security features not supported.",                       # x.7.4
        "Cryptographic failure.",                                 # x.7.5
        "Cryptographic algorithm not supported.",                 # x.7.6
        "Message integrity failure.",                             # x.7.7
    ),
)

def _status(return_):
    if return_ in (902, 904):
        return 4
    elif return_ in (901, 903):
        return 5
    elif return_ in (900, 910):
        return 2
    else:
        return 4

def _dsn(return_, reason, default, subject, detail):
    if not return_:
        return_ = default
    elif not type(return_) is int:
        reason = return_
        return_ = default

    if not reason:
        try:
            msg = RFC1893[subject][detail]
        except KeyError:
            detail = 0
            try:
                msg = RFC1893[subject][detail]
            except KeyError:
                subject = 0
                msg = RFC1893[subject][detail]
    else:
        msg = reason

    class_ = _status(return_)
    return (return_, '%s (#%d.%d.%d)' % (msg, class_, subject, detail))

_status_codes = [
    ('unspecified',             DENYSOFT,   0, 0),
    ('addr_unspecified',        DENYSOFT,   1, 0),
    ('no_such_user',            DENYSOFT,   1, 0),
    ('addr_bad_dest_mbox',      DENY,       1, 1),
    ('addr_bad_dest_system',    DENY,       1, 2),
    ('addr_bad_dest_syntax',    DENY,       1, 3),
    ('addr_bad_dest_ambigous',  DENYSOFT,   1, 4),
    ('addr_rcpt_ok',            OK,         1, 5),
    ('addr_mbox_moved',         DENY,       1, 6),
    ('addr_bad_from_syntax',    DENY,       1, 7),
    ('addr_bad_from_system',    DENY,       1, 8),
    ('mbox_unspecified',        DENYSOFT,   2, 0),
    ('mbox_disabled',           DENY,       2, 1),
    ('mbox_full',               DENYSOFT,   2, 2),
    ('mbox_msg_too_long',       DENY,       2, 3),
    ('mbox_list_expansion_problem', DENYSOFT, 2, 4),
    ('sys_unspecified',         DENYSOFT,   3, 0),
    ('sys_disk_full',           DENYSOFT,   3, 1),
    ('sys_not_accepting_mail',  DENYSOFT,   3, 2),
    ('sys_not_supported',       DENYSOFT,   3, 3),
    ('sys_msg_too_big',         DENY,       3, 4),
    ('net_unspecified',         DENYSOFT,   4, 0),
    ('temp_resolver_failed',    DENYSOFT,   4, 3),
    ('net_directory_server_failed', DENYSOFT, 4, 3),
    ('net_system_congested',    DENYSOFT,   4, 5),
    ('net_routing_loop',        DENY,       4, 6),
    ('too_many_hops',           DENY,       4, 6),
    ('proto_unspecified',       DENYSOFT,   5, 0),
    ('proto_invalid_command',   DENY,       5, 1),
    ('proto_syntax_error',      DENY,       5, 2),
    ('proto_rcpt_list_too_long', DENYSOFT,  5, 3),
    ('too_many_rcpts',          DENYSOFT,   5, 3),
    ('proto_invalid_cmd_args',  DENY,       5, 4),
    ('proto_wrong_version',     DENYSOFT,   5, 5),
    ('media_unspecified',       DENYSOFT,   6, 0),
    ('media_unsupported',       DENY,       6, 1),
    ('media_conv_prohibited',   DENY,       6, 2),
    ('media_conv_unsupported',  DENYSOFT,   6, 3),
    ('media_conv_lossy',        DENYSOFT,   6, 4),
    ('sec_unspecified',         DENYSOFT,   7, 0),
    ('sec_sender_unauthorized', DENY,       7, 1),
    ('bad_sender_ip',           DENY,       7, 1),
    ('relaying_denied',         DENY,       7, 1),
    ('sec_list_dest_prohibited', DENY,      7, 2),
    ('sec_conv_failed',         DENY,       7, 3),
    ('sec_feature_unsupported', DENY,       7, 4),
    ('sec_crypto_failure',      DENY,       7, 5),
    ('sec_crypto_algorithm_unsupported', DENYSOFT, 7, 6),
    ('sec_msg_integrity_failure', DENY,     7, 7),
]

_alternatives = {
    'no_such_user': 'No such user',
    'temp_resolver_failed': 'Temporary address resolution failure',
    'too_many_hops': 'Too many hops',
    'bad_sender_ip': "Bad sender's IP",
    'relaying_denied': 'Relaying denied'
}

_module = sys.modules[__name__]
for name, default, subject, detail in _status_codes:
    alt = _alternatives.get(name, None)
    method = 'def %s(return_=None, reason=None):'
    if not alt:
        method += '    return _dsn(return_, reason, %d, %d, %d)'
        exec (method % (name, default, subject, detail)) in globals()
    else:
        method += '    return _dsn(return_, reason or %r, %d, %d, %d)'
        exec (method % (name, alt, default, subject, detail)) in globals()
