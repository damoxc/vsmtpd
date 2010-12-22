#
# vsmtpd/smtp.py
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

import logging

from vsmtpd.error import (HookNotFoundError, HookError, DenyError, DenySoftError,
    DenyDisconnectError, DenySoftDisconnectError)

log = logging.getLogger(__name__)

def hook(func):
    """
    Decorator to mark a method as a hook handler.
    """
    func._hook_name = func.func_name
    return func

class Hook(object):
    """
    Base class for a hook handler.

    :param name: The hook name
    :type name: str
    """

    errors = []

    def __init__(self, name):
        self.__name = name
        self.__callbacks = []

    def add_handler(self, callback):
        """
        Add a handler to the hook.

        :param callback: The hook callback
        :type callback: function
        """
        self.__callbacks.append(callback)

    def default(self, *args, **kwargs):
        """
        Default action that does nothing.
        """

    def error(self, smtp, error):
        """
        Handles any errors raised within the callback, allowing a hook
        to change the behaviour for errors depending on what it is.
        """

    def handle(self, smtp, *args, **kwargs):
        """
        Default handler that loops over the callbacks calling them one at 
        a time.
        """
        for callback in self.__callbacks:
            try:
                callback(*args, **kwargs)
            except HookError as e:
                return self.error(smtp, e)
            except Exception as e:
                log.exception(e)

    def remove_handler(self, callback):
        """
        Remove a handler from the hook.

        :param callback: The callback to remove
        :type callback: function
        """
        self.__callbacks.remove(callback)

    @property
    def name(self):
        """
        The hooks name
        """
        return self.__name

class PreConnection(Hook):

    def __init__(self):
        super(PreConnection, self).__init__('pre_connection')

    def error(self, smtp, error):
        """
        This handler disconnects the client.
        """
        if issubclass(error, (DenyError, DenySoftError)):
            smtp.disconnect(error.code, error.message)

class Connect(Hook):

    def __init__(self):
        super(Connect, self).__init__('connect')

    def error(self, smtp, error):
        """
        This handler disconnects the client.
        """
        if issubclass(error, (DenyError, DenySoftError)):
            smtp.disconnect(error.code, error.message)

class PostConnection(Hook):

    def __init__(self):
        super(PostConnection, self).__init__('post_connection')

class Greeting(Hook):

    def __init__(self):
        super(Greeting, self).__init__('greeting')

class Helo(Hook):

    def __init__(self):
        super(Helo, self).__init__('helo')

class Ehlo(Hook):

    def __init__(self):
        super(Ehlo, self).__init__('ehlo')

class ResetTransaction(Hook):

    def __init__(self):
        super(ResetTransaction, self).__init__('reset_transaction')

class Mail(Hook):

    def __init__(self):
        super(Mail, self).__init__('mail')

class Rcpt(Hook):

    def __init__(self):
        super(Rcpt, self).__init__('rcpt')

class Data(Hook):

    def __init__(self):
        super(Data, self).__init__('data')

class DataPost(Hook):

    def __init__(self):
        super(DataPost, self).__init__('data_post')

class QueuePre(Hook):

    def __init__(self):
        super(QueuePre, self).__init__('queue_pre')

class Queue(Hook):

    def __init__(self):
        super(Queue, self).__init__('queue')

class QueuePost(Hook):

    def __init__(self):
        super(QueuePost, self).__init__('queue_post')

class Quit(Hook):
    
    def __init__(self):
        super(Quit, self).__init__('quit')

class Disconnect(Hook):

    def __init__(self):
        super(Disconnect, self).__init__('disconnect')

class UnrecognizedCommand(Hook):

    def __init__(self):
        super(UnrecognizedCommand, self).__init__('unrecognized_command')

class Vrfy(Hook):

    def __init__(self):
        super(Vrfy, self).__init__('vrfy')

class Deny(Hook):

    def __init__(self):
        super(Deny, self).__init__('deny')

class Ok(Hook):

    def __init__(self):
        super(Ok, self).__init__('ok')

class Auth(Hook):

    def __init__(self):
        super(Auth, self).__init__('auth')

class AuthPlain(Hook):

    def __init__(self):
        super(AuthPlain, self).__init__('auth-plain')

class AuthLogin(Hook):
    
    def __init__(self):
        super(AuthLogin, self).__init__('auth-login')

class AuthCramMD5(Hook):

    def __init__(self):
        super(AuthCramMD5, self).__init__('auth-cram-md5')

class HookManager(object):
    """
    Manage dispatching hook calls off to the correct places.
    """

    def __init__(self):
        self.__hooks = {}

        # Create all the hooks
        for hook in Hook.__subclasses__():
            hook = hook()
            self.__hooks[hook.name] = hook

    def deregister(self, hook_name, callback):
        """
        Deregister a hook listener from the hook manager.

        :param hook_name: The name of the hook to deregister
        :type hook_name: str
        :param callback: The hook callback to degregister
        :type callback: func
        """

        if hook_name not in self.__hooks:
            raise HookNotFoundError(hook_name)
        self.__hooks[hook_name].remove_handler(callback)

    def register(self, hook_name, callback):
        """
        Register a hook listener with the hook manager.
        
        :param hook_name: The name of the hook to listen for
        :type hook_name: str
        :param callback: The hook callback function
        :type callback: func
        """
        if hook_name not in self.__hooks:
            raise HookNotFoundError(hook_name)
        self.__hooks[hook_name].add_handler(callback)

    def dispatch(self, smtp, hook_name, *args, **kwargs):
        """
        Fires a hook.

        :param smtp: The instance of the SMTP calling the hook
        :type smtp: vsmtpd.smtpd.SMTP
        :param hook_name: The name of the hook to call
        :type hook_name: str
        """
        if hook_name not in self.__hooks:
            raise HookNotFoundError(hook_name)
        self.__hooks[hook_name].handle(smtp, *args, **kwargs)

    def scan_plugin(self, plugin):
        """
        Scans a plugin for any hook handlers.

        :param plugin: The plugin object
        :type plugin: object
        """

        # Loop over the plugins attributes checking to see if they are
        # hook handlers.
        for attr in dir(plugin):
            hook_name = getattr(getattr(plugin, attr), '_hook_name', None)
            if not hook_name:
                continue
            # Register the hook handler
            self.register(hook_name, getattr(plugin, attr))
