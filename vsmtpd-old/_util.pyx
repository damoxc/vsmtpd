#
# vsmtpd/_util.pyx
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

from libc.stdio cimport sprintf
from libc.string cimport strlen, strncpy, strtok

def reverse_ip(char *ip):
    cdef int ret
    cdef char _ip[16], *p1, *p2, *p3, *p4, rip[16]

    # Ensure that the IP address isn't too long.
    if strlen(_ip) > 15:
        raise ValueError('Invalid IP address: too short')

    # Take a copy of the IP address to manipulate so we don't mess up the
    # original string.
    strncpy(_ip, ip, 15)

    # Split the IP address into its parts.
    p1 = strtok(_ip, '.')
    p2 = strtok(NULL, '.')
    p3 = strtok(NULL, '.')
    p4 = strtok(NULL, '.')

    if p1 == NULL or p2 == NULL or p3 == NULL or p4 == NULL:
        raise ValueError('Invalid IP address: missing parts')

    # Normally using snprintf here would be wise but since there is a
    # previous check for the length of the string we are splitting and
    # reversing, it's safe to use sprintf in this instance as it is faster.
    sprintf(rip, "%s.%s.%s.%s", p4, p3, p2, p1)

    return rip
