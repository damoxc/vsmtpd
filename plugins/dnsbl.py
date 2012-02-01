#
# dnsbl.py
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

"""
dnsbl - handle DNS BlackList lookups

Plugin tha checks the IP address of the incoming connection against a
configuration set of RBL services.
"""

import os
import gevent
import logging

from gevent.dns import DNSError
from gevent.socket import gethostbyname

from vsmtpd.hooks import hook
from vsmtpd.plugins.plugin import PluginBase
from vsmtpd.util import reverse_ip

log = logging.getLogger(__name__)

def check_dnsbl(rip, bl):
    try:
        return gethostbyname('%s.%s' % (rip, bl))
    except DNSError:
        return None

class Plugin(PluginBase):

    def __init__(self, config=None):
        self.disconnect = False
        if config and 'disconnect' in config:
            self.disconnect = config.getboolean('disconnect')

    @hook
    def connect(self, connection):
        remote_ip   = connection.remote_ip
        reversed_ip = reverse_ip(remote_ip)

        jobs = []
        for dnsbl in self.simple_config('dnsbl_zones'):
            jobs.append(gevent.spawn(check_dnsbl, reversed_ip, dnsbl))

        connection.notes['dnsbl_jobs'] = jobs

    @hook
    def rcpt(self, transaction, rcpt, **param):
        jobs = transaction.connection.notes.get('dnsbl_jobs')
        gevent.joinall(jobs)
        ip = transaction.connection.remote_ip
        #if any([j.value for j in jobs]):
        self.deny(None, self.disconnect)
