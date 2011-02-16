#
# vsmtpd/commands.py
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

class Command(object):
    
    @classmethod
    def parse(cls, connection, line):
        raise NotImplementedError

    @classmethod
    def respond(cls, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def getall():
        return Command.__subclasses__()

class Helo(Command):

    @classmethod
    def parse(cls, connection, line):
        (code, message) = connection.fire('helo_parse')
        print code, message

    @classmethod
    def response(cls, transaction, host):
        pass

class Ehlo(Command):
    
    @classmethod
    def parse(cls, connection, line):
        pass

    @classmethod
    def response(cls, transaction, host):
        pass

class Mail(Command):

    @classmethod
    def parse(cls, connection, line):
        pass

class Rcpt(Command):

    @classmethod
    def parse(cls, connection, line):
        pass

class Auth(Command):

    @classmethod
    def parse(cls, connection, line):
        pass

class Data(Command):

    @classmethod
    def parse(cls, connection, line):
        pass

class Rset(Command):

    @classmethod
    def parse(cls, connection, line):
        pass

class Help(Command):

    @classmethod
    def parse(cls, connection, line):
        pass

class Vrfy(Command):

    @classmethod
    def parse(cls, connection, line):
        pass

class Noop(Command):

    @classmethod
    def parse(cls, connection, line):
        pass

class Quit(Command):

    @classmethod
    def parse(cls, connection, line):
        pass
