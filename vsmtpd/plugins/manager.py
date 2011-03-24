#
# vsmtpd/plugins/manager.py
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

import imp
import sys

from vsmtpd.error import PluginNotFoundError
from vsmtpd.plugins.plugin import PluginBase

class PluginManager(object):
    """
    A simple class that handles loading plugins mostly through use of the imp
    module.

    At some point down the line this may be extended to add support for eggs
    and maybe other functionality but currently only single module plugins
    are supported.

    :keyword path: The python path to use when trying to find the module
    :type path: list of str
    """

    def __init__(self, path=None):
        self.path = path
        self.plugins = {}
    
    def load(self, plugin_name):
        """
        Load a plugin of the specified name and return the plugin
        class.

        :param plugin_name: The name of the plugin module
        :type plugin_name: str
        """

        fp, path, description = imp.find_module(plugin_name, self.path)
        try:
            module = imp.load_module('vsmtpd.plugins.%s' % plugin_name, fp,
                                     path, description)
        finally:
            fp.close()

        plugin_cls = getattr(module, 'Plugin', None)
        if not plugin_cls:
            raise PluginNotFoundError("Can't find a plugin in the module")

        return plugin_cls
