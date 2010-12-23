#
# vsmtpd/common.py
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

OK                  = 900
DENY                = 901 # 550
DENYSOFT            = 902 # 450
DENY_DISCONNECT     = 903 # 550 + disconnect
DENYSOFT_DISCONNECT = 904 # 450 + disconnect
DECLINED            = 909
DONE                = 910
YIELD               = 911

class Connection(object):

    def __init__(self, smtp):
        self.__smtp = smtp
        self.__hello = None
        self.__hello_host = None

    @property
    def hello(self):
        return self.__hello

    @hello.setter
    def hello(self, value):
        self.__hello = value

    @property
    def hello_host(self):
        return self.__hello_host

    @hello_host.setter
    def hello_host(self, value):
        self.__hello_host = value

    @property
    def local_ip(self):
        return self.__smtp.transport.getHost().host

    @property
    def local_port(self):
        return self.__smtp.transport.getHost().port

    @property
    def remote_ip(self):
        return self.__smtp.transport.getPeer().host

    @property
    def remote_port(self):
        return self.__smtp.transport.getPeer().port

    @property
    def relay_client(self):
        return False

    def sendCode(self, code, message=''):
        return self.__smtp.sendCode(code, message)

class Transaction(object):

    def __init__(self, connection):
        self.__connection = connection
        self.__sender = None

    @property
    def connection(self):
        return self.__conection

    @property
    def sender(self):
        return self.__sender

    @sender.setter
    def sender(self, value):
        self.__sender = value
