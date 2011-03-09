#
# vsmtpd/hooks.py
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

from types import FunctionType
from vsmtpd.error import HookNotFoundError

HOOKS = [ 
# SMTP hooks
    'pre_connection',       # after the connection is accepted
    'connect',              # at the start of a connection before the
                            # greeting is sent
    'post_connection',      # directly before the connection is finished or
                            # if the client drops the connection.
    'greeting',             # allows plugins to modify the greeting
    'logging',              # when a log message is written
    'config',               # when a config ``file`` is requested
    'helo',                 # after the client sends HELO
    'ehlo',                 # after the client sends EHLO
    'reset_transaction',    # after the transaction is reset
    'mail',                 # after the client sends the mail from command
    'rcpt',                 # after the client sends a RCPT TO: command
    'data',                 # after the client sends the DATA command
    'data_post',            # after the client sent the final ".\r\n" of a 
                            # message.
    'queue_pre',            # prior to the message being queued
    'queue',                # used to queue the message
    'queue_post',           # after the message has been queued
    'quit',                 # after the client sent a QUIT command
    'disconnect',           # after a plugin returned DENY(|SOFT)_DISCONNECT
                            # or after the client sent the QUIT command
    'unrecognized_command', # if the client sends an unkonwn command
    'vrfy',                 # if the client sends the VRFY command
    'deny',                 # after a plugin returned DENY, DENYSOFT
    'ok',                   # after a plugin did not return DENY, etc.
    'auth',                 #
    'auth-plain',           #
    'auth-login',           #
    'auth-cram-md5',        #

# Parsing hooks
    'helo_parse',
    'ehlo_parse',
    'mail_parse',
    'rcpt_parse',
    'auth_parse'
]

def hook(hook_name):
    """
    Specify a method has a hook handler.
    """
    if type(hook_name) is FunctionType:
        hook_name._is_hook = True
        hook_name._hook_name = hook_name.func_name
        return hook_name

    def wrapper(func):
        func._is_hook = True
        func._hook_name = hook_name
        return func
    return wrapper

class HookManager(object):
    """ 
    Manage dispatching hook calls off to the correct places.
    """

    def __init__(self):
        self.__hooks = dict([(h, []) for h in HOOKS])

    def deregister_hook(self, hook_name, callback):
        """
        Deregister a hook from the hook manager.

        :param hook_name: The name of the hook to deregister
        :type hook_name: str
        :param callback: The hook callback to degregister
        :type callback: func
        """
        if hook not in self.__hooks:
            raise HookNotFoundError(hook_name)
        self.__hooks[hook_name].remove(callback)

    def register_hook(self, hook_name, callback):
        """
        Register a hook listener with the hook manager.
        
        :param hook_name: The name of the hook to listen for
        :type hook_name: str
        :param callback: The hook callback function
        :type callback: func
        """
        if hook not in self.__hooks:
            raise HookNotFoundError(hook_name)
        self.__hooks[hook_name].append(callback)

    def dispatch_hook(self, hook_name, *args, **kwargs):
        """
        Fires a hook.

        :param hook_name: The name of the hook to call
        :type hook_name: str
        """
        for cb in self.__hooks[hook_name]:
            cb(*args, **kwargs)
