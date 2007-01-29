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
import machine
from freevo.ui import config
import logging

log = logging.getLogger('games')


class GameItem(MediaItem):
    """
    This is a virtual representation of the rom.
    """
    def __init__(self, parent, url, gi_ind, imgpath):
        MediaItem.__init__(self, parent, type='games')
        self.set_url(url)
        self.__emu = None
        self.__ind = gi_ind

        # try to load a screen shot if it is available...
        try:
            import kaa.imlib2, zipfile

            shot = url.basename.split('.')[0] + '.png'

            if '.zip' in imgpath[-4:]:
                zf = zipfile.ZipFile(imgpath)
                self.image = kaa.imlib2.open_from_memory(zf.read(shot))
            else:
                self.image = imgpath + '/' + shot
        except:
            self.image = None


    def actions(self):
        items = [Action(_('Play'), self.play)]
        return items


    def play(self):
        self.__emu = machine.emu(self)
        self.__emu.launch(self)


    def get_ind(self):
        return self.__ind


    gi_ind = property(get_ind, None)
