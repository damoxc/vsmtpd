#
# vsmtpd/plugins/plugin.py
#
# Copyright (C) 2010 Damien Churchill <damoxc@gmail.com>
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

from vsmtpd.config import load_config, load_simple_config
from vsmtpd.error import (
    DenyError,
    DenySoftError,
    DenyDisconnectError,
    DenySoftDisconnectError,
    DoneError,
    OkayError
)

class PluginBase(object):

    def declined(self):
        return None

    def deny(self, message=None, disconnect=False):
        if disconnect:
            raise DenyDisconnectError(message)
        else:
            raise DenyError(message)

    def deny_soft(self, message=None, disconnect=False):
        if disconnect:
            raise DenySoftDisconnectError(message)
        else:
            raise DenySoftError(message)

    def done(self, message=None):
        raise DoneError(message)

    def config(self, name, defaults=None):
        """
        Loads a configuration file using SafeConfigParser and returns the
        resulting Config object.

        :param name: The name of the configuration file
        :type name: str
        """
        return load_config(name, defaults)

    def simple_config(self, name):
        """
        Gets a simple configuration file and returns it as a list.
        
        :param name: The name of the configuration file
        :type name: str
        """
        return load_simple_config(name)

    def ok(self, message=None):
        raise OkayError(message)
