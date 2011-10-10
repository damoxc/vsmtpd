#
# check_loop.py
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

import logging

from vsmtpd import dsn
from vsmtpd.hooks import hook
from vsmtpd.plugins.plugin import PluginBase

log = logging.getLogger(__name__)

class Plugin(PluginBase):

    def __init__(self, config=None):
        self.max_hops = 100

        if config:
            max_hops = config.getint('max_hops')
            if max_hops:
                self.max_hops = max_hops

    @hook
    def data_post(self, transaction):
        hops = 0
        for key in transaction.headers.keys():
            if key.lower() in ('received', 'delivered-to'):
                hops += 1

        if hops > self.max_hops:
            return dsn.too_many_hops()
