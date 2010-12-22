#
# vsmtpd/plugins/core/setup.py
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

from setuptools import setup, find_packages

setup (
    name         = 'Core',
    version      = '0.0.1',
    description  = 'Collection of core plugins to extend vsmtpd',
    author       = 'Damien Churchill',
    author_email = 'damoxc@gmail.com',
    url          = 'http://vsmtpd.damoxc.net',
    license      = 'GPLv3',
    long_description = '',
    packages     = find_packages(),
    namespace_packages = ['vsmtpd', 'vsmtpd.plugins'],
    package_data = {},

    entry_points = {
        'vsmtpd.plugins': [
            'count_unrecognized_commands = vsmtpd.plugins.core.count_unrecognized_commands:CountUnrecognizedCommands',
            'hosts_allow = vsmtpd.plugins.core.hosts_allow:HostsAllow',
            'quit_fortune = vsmtpd.plugins.core.quit_fortune:QuitFortune'
        ]
    }
)
