#
# vsmtpd/config.py
#
# Copyright (C) 2010-2011 Damien Churchill <damoxc@gmail.com>
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

import os
import sys
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import collections
import ConfigParser

CONFIG_DIR = '/etc/vsmtpd'

class ConfigWrapper(object):

    def __init__(self, config, section):
        self.__config = config
        self.__section = section

    def get(self, option):
        return self.__config.get(self.__section, option)

    def getint(self, option):
        return self.__config.getint(self.__section, option)

    def getfloat(self, option):
        return self.__config.getfloat(self.__section, option)

    def getboolean(self, option):
        return self.__config.getboolean(self.__section, option)

    def has_option(self, option):
        return self.__config.has_option(self.__section, option)

    def items(self):
        return self.__config.items(self.__section)

    def options(self):
        return self.__config.options(self.__section)

    def set(self, option, value):
        return self.__config.set(self.__section, option, value)

    def __contains__(self, item):
        return self.has_option(item)

    def __iter__(self):
        return iter(self.__config)

if sys.version_info < (2, 7):
    from UserDict import DictMixin

    class OrderedDict(dict, DictMixin):

        def __init__(self, *args, **kwds):
            if len(args) > 1:
                raise TypeError('expected at most 1 arguments, got %d' % len(args))
            try:
                self.__end
            except AttributeError:
                self.clear()
            self.update(*args, **kwds)

        def clear(self):
            self.__end = end = []
            end += [None, end, end]         # sentinel node for doubly linked list
            self.__map = {}                 # key --> [key, prev, next]
            dict.clear(self)

        def __setitem__(self, key, value):
            if key not in self:
                end = self.__end
                curr = end[1]
                curr[2] = end[1] = self.__map[key] = [key, curr, end]
            dict.__setitem__(self, key, value)

        def __delitem__(self, key):
            dict.__delitem__(self, key)
            key, prev, next = self.__map.pop(key)
            prev[2] = next
            next[1] = prev

        def __iter__(self):
            end = self.__end
            curr = end[2]
            while curr is not end:
                yield curr[0]
                curr = curr[2]

        def __reversed__(self):
            end = self.__end
            curr = end[1]
            while curr is not end:
                yield curr[0]
                curr = curr[1]

        def popitem(self, last=True):
            if not self:
                raise KeyError('dictionary is empty')
            if last:
                key = reversed(self).next()
            else:
                key = iter(self).next()
            value = self.pop(key)
            return key, value

        def __reduce__(self):
            items = [[k, self[k]] for k in self]
            tmp = self.__map, self.__end
            del self.__map, self.__end
            inst_dict = vars(self).copy()
            self.__map, self.__end = tmp
            if inst_dict:
                return (self.__class__, (items,), inst_dict)
            return self.__class__, (items,)

        def keys(self):
            return list(self)

        setdefault = DictMixin.setdefault
        update = DictMixin.update
        pop = DictMixin.pop
        values = DictMixin.values
        items = DictMixin.items
        iterkeys = DictMixin.iterkeys
        itervalues = DictMixin.itervalues
        iteritems = DictMixin.iteritems

        def __repr__(self):
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, self.items())

        def copy(self):
            return self.__class__(self)

        @classmethod
        def fromkeys(cls, iterable, value=None):
            d = cls()
            for key in iterable:
                d[key] = value
            return d

        def __eq__(self, other):
            if isinstance(other, OrderedDict):
                return len(self)==len(other) and self.items() == other.items()
            return dict.__eq__(self, other)

        def __ne__(self, other):
            return not self == other

else:
    OrderedDict = collections.OrderedDict

def _dict_to_defaults(sections):
    fp = StringIO.StringIO()
    for name, section in sections.iteritems():
        fp.write('[%s]\n' % name)
        for key, value in section.iteritems():
            if value is None:
                value = ''
            fp.write('%s = %s\n' % (key, value))
        fp.write('\n')
    fp.seek(0)
    return fp

def load_config(name, defaults=None):
    path = name if os.path.exists(name) else os.path.join(CONFIG_DIR, name)
    config = ConfigParser.SafeConfigParser(dict_type=OrderedDict)
    if defaults:
        config.readfp(_dict_to_defaults(defaults))
    config.read(path)
    return config

def load_simple_config(name):
    path = os.path.join(CONFIG_DIR, name)
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            yield line
