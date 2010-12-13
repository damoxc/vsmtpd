#!/usr/bin/env python
#
# setup.py
#
# Copyright (C) 2010 @UK Plc, http://www.uk-plc.net
#
# Author:
#   2010 Damien Churchill <damoxc@gmail.com>
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

from setuptools import setup, find_packages

setup(
    name         = 'vmsmtpd',
    version      = '0.0.1',
    author       = 'Damien Churchill',
    author_email = 'damoxc@gmail.com',

    packages     = find_packages(exclude=['tests', 'docs']),
    entry_points = {
        'console_scripts': [
            'vsmtpd = vsmtpd.daemon:main'
        ]
    }
)
