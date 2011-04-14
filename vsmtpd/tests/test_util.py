#
# vsmtpd/tests/test_util.py
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

from vsmtpd.util import NoteObject
from vsmtpd.tests.common import TestCase

class NoteObjectTestCase(TestCase):

    def test_note_object(self):
        note = NoteObject()
        self.assertEqual(note._notes, None)

        note.notes['test'] = 5
        self.assertEqual(type(note._notes), dict)
        self.assertEqual(note._notes['test'], 5)
        self.assertEqual(note.notes['test'], 5)

        note.notes['example'] = 17
        self.assertEqual(note.notes['test'], 5)
        self.assertEqual(note.notes['example'], 17)
