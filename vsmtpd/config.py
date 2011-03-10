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
import ConfigParser

CONFIG_DIR = '/etc/vsmtpd'

def load_config(name):
    path = os.path.join(CONFIG_DIR, name)
    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    config.read(path)
    return config

def load_simple_config(name):
    path = os.path.join(CONFIG_DIR, name)
    if not os.path.exists(path):
        return []

    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        yield line
