#
# vsmtpd/config.py
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

import json

class Config(object):
    
    def __init__(self, path, defaults=None):
        self.path = path
        if defaults:
            self.__config = defaults
        else:
            self.__config = {}

    def load(self, path=None):
        """
        Load the configuration from the config file.

        :keyword path: The optional path parameter
        :type path: str
        """

        if path is None:
            path = self.path

        self.__config.update(json.load(open(path)))

def load(path):
    config = Config(path)
    return config
