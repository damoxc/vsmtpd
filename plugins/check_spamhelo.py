#
# check_spamhelo.py
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
check_spamhelo - Check a HELO message delivered from a connecting host.

Check a HELO message delivered from a connection host. Reject any that
appear in the badhelo config -- e.g. yahoo.com and aol.com which neither
the real Yahoo or the real AOL use, but which spammers use rather a lot.

Add domains or hostnames to the badhelo configuraiton file; one per line.

Based off the check_spamhelo plugin distributed with qpsmtpd.
"""

class Plugin(PluginBase):

    @hook('helo', 'ehlo')
    def spamhelo(self, transaction, host):
        for bad in self.simple_config('badhelo'):
            if host != bad.lower():
                continue
            log.debug('Denying HELO from host claiming to be %s', bad)
            self.deny("Sorry I don't believe that you are %s" % host, True)
