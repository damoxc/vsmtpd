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

from vsmtpd.common import DECLINED, DONE, OK
from vsmtpd.config import load_config, load_simple_config

class Plugin(object):

    def declined(self):
        return DECLINED

    def done(self, message=None):
        return (DONE, message)

    def config(self, name):
        """
        Loads a configuration file using SafeConfigParser and returns the
        resulting Config object.

        :param name: The name of the configuration file
        :type name: str
        """
        return load_config(name)

    def simple_config(self, name):
        """
        Gets a simple configuration file and returns it as a list.
        
        :param name: The name of the configuration file
        :type name: str
        """
        return load_simple_config(name)

    def ok(self, message=None):
        return (OK, message)
