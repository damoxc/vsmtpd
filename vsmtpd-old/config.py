#
# vsmtpd/config.py
#
# Copyright (C) 2010-2011 Damien Churchill <damoxc@gmail.com>
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

import os
import cStringIO as StringIO
import ConfigParser

from vsmtpd.util import OrderedDict

CONFIG_DIR = '/etc/vsmtpd'

class ConfigWrapper(object):
    """
    Wraps a ConfigParser object and exposes the same API however only
    for a single section. It's useful if the same config object is
    shared in multiple places and the section name may be changed
    later on.
    """

    def __init__(self, config, section):
        self.__config = config
        self.__section = section

    def get(self, option):
        return self.__config.get(self.__section, option)

    def getint(self, option):
        return self.__config.getint(self.__section, option)

    def getfloat(self, option):
        return self.__config.getfloat(self.__section, option)

    def getboolean(self, option):
        return self.__config.getboolean(self.__section, option)

    def has_option(self, option):
        return self.__config.has_option(self.__section, option)

    def items(self):
        return self.__config.items(self.__section)

    def options(self):
        return self.__config.options(self.__section)

    def set(self, option, value):
        return self.__config.set(self.__section, option, value)

    def __contains__(self, item):
        return self.has_option(item)

def _dict_to_defaults(sections):
    fp = StringIO.StringIO()
    for name, section in sections.iteritems():
        fp.write('[%s]\n' % name)
        for key, value in section.iteritems():
            if value is None:
                value = ''
            fp.write('%s = %s\n' % (key, value))
        fp.write('\n')
    fp.seek(0)
    return fp

def load_config(name, defaults=None):
    path = name if os.path.exists(name) else os.path.join(CONFIG_DIR, name)
    config = ConfigParser.SafeConfigParser(dict_type=OrderedDict)
    if defaults:
        config.readfp(_dict_to_defaults(defaults))
    config.read(path)
    return config

def load_simple_config(name):
    path = name if os.path.exists(name) else os.path.join(CONFIG_DIR, name)
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            yield line
