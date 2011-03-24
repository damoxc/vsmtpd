#
# random_error.py
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
#

import random
import logging

from vsmtpd.hooks import hook
from vsmtpd.plugins.plugin import PluginBase

log = logging.getLogger(__name__)

class Plugin(PluginBase):

    def __init__(self, config):
        self.likelyhood = config.getfloat('likelyhood')

    @hook
    def connect(self, connection):
        connection.notes['random_fail_%'] = self.likelyhood
        self.random_fail()

    @hook
    def helo(self, *args):
        self.random_fail()

    @hook
    def ehlo(self, *args):
        self.random_fail()

    @hook
    def mail(self, *args):
        self.random_fail()

    @hook
    def rcpt(self, *args):
        self.random_fail()

    @hook
    def data(self, *args):
        self.random_fail()

    @hook
    def data_post(self, *args):
        self.random_fail()

    def random_fail(self):
        prob = 1 - self.likelyhood
        log.info('to fail, random() must be more than %f', prob ** (1.0 / 6))
        if random.random() < (prob ** (1.0 / 6)):
            return

        self.deny_soft('random failure', disconnect=random.randint(0, 5) < 2)
