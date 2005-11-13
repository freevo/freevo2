# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# emulator.py - the Freevo game item.
# -----------------------------------------------------------------------------
#
# This class is used to display roms in the freevo menu.  It also connects the
# roms to the correct emulators.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dan Casimiro <dan.casimiro@gmail.com>
# Maintainer:    Dan Casimiro <dan.casimiro@gmail.com>
#
# Please see the file doc/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------------
from menu import MediaItem, Action

class GameItem(MediaItem):
    """
    This is a virtual representation of the rom.
    """
    def __init__(self, parent, url, system):
        MediaItem.__init__(self, parent, type='games')
        self.set_url(url)
        self.__emu = None
        self.__sys = system

        # try to load a screen shot if it is available...
        try:
            import kaa.imlib2, zipfile, os.path
            (path, name) = (url.dirname, url.basename)
            # TODO: Change hard coded mame path to a more general case...
            # TODO: cache screen shots ?
            snaps = zipfile.ZipFile(os.path.join(path, '../snap/snap.zip'))
            shotname = name.split('.')[0] + '.png'
            self.image = kaa.imlib2.open_from_memory(snaps.read(shotname))
        except:
            pass

    def actions(self):
        items = [Action(_('Play'), self.play)]
        return items

    def play(self):
        from factory import Factory
        self.__emu = Factory().player(self)
        self.__emu.launch(self)

    def get_system(self):
        return self.__sys

    system = property(get_system, None)
