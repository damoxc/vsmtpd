#
# vsmtpd/error.py
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

class Error(Exception):
    pass

class TimeoutError(Error):
    pass

class HookNotFoundError(Error):
    pass

class PluginNotFoundError(Error):
    pass

class CommandParseError(Error):
    pass

class AddressParseError(Error):
    pass


# The below are used to allow for hooks to have an impact upon the SMTP
# conversation. They are able to raise these errors and stop hooks from
# running.
class HookError(Error):
    soft = False
    disconnect = False
    done = False
    okay = False
    
    @property
    def message(self):
        return self.args[0] if self.args else ''

class StopHooksError(HookError):
    pass

class OkayError(StopHooksError):
    okay = True

class DoneError(StopHooksError):
    done = True

class DenyError(HookError):
    pass

class DenySoftError(HookError):
    soft = True

class DisconnectError(HookError):
    disconnect = True

class DenyDisconnectError(DenyError, DisconnectError):
    pass

class DenySoftDisconnectError(DenySoftError, DisconnectError):
    pass
