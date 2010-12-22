#
# vsmtpd/daemon.py
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

# Stop Ubuntu spitting out pointless deprecation warnings we can do nothing
# about.
import warnings
warnings.filterwarnings('ignore',
    category = DeprecationWarning,
    module   = 'twisted')

import os
import grp
import pwd
import logging

from optparse import OptionParser
from twisted.internet import reactor

from vsmtpd.smtpd import SMTPD

log = logging.getLogger(__name__)

class Daemon(object):

    def __init__(self, options, args):
        self.smtpd = SMTPD()
        self.smtpd.interfaces = options.listen
        self.smtpd.port = options.port
        self.children = []
        self.master = True
    
    def start(self):
        """
        Start the daemon and perform all actions to prepare vsmtpd for
        accepting mail.
        """
        # Hack until proper logging configuration is added
        logging.basicConfig(
            level  = logging.INFO,
            format = '%(asctime)s [%(levelname)s] %(message)s'
        )

        self.smtpd.start()
        #reactor.callLater(0, self.spawn_children)
        reactor.run()

    def spawn_children(self):
        """
        Starts the children ready for processing
        """

        for i in xrange(1, 3):
            child_pid = os.fork()
            if child_pid == 0:
                self.master = False
                break
            else:
                self.children.append(child_pid)

        if self.master:
            print 'master pid: %s' % os.getpid()
            for child in self.children:
                print 'child pid: %s' % child

def main():
    parser = OptionParser()
    parser.add_option('-l', '--listen', dest='listen',  action='append',
        help='listen on this address')
    parser.add_option('-p', '--port', dest='port', type='int', default=25,
        help='set the default port to listen on')
    (options, args) = parser.parse_args()

    daemon = Daemon(options, args)
    daemon.start()
