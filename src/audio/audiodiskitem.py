# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# audiodiskitem.py - Item for CD Audio Disks
# -----------------------------------------------------------------------------
# $Id$
#
# This file handles and item for an audio cd. When selected it will
# either play the whole disc or show a menu with all items.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2006 Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

__all__ = [ 'AudioDiskItem' ]

# Python imports
import os

# Freevo imports
from freevo.ui.config import config

from freevo.ui.menu import Action, Menu
from audioitem import AudioItem
from freevo.ui.playlist import Playlist
from freevo.ui.directory import DirItem


class AudioDiskItem(Playlist):
    """
    Class for handling audio disks.
    """
    def __init__(self, device, parent):
        Playlist.__init__(self, parent=parent, type='audio')
        self.type = 'audiocd'
        self.info = device
        self.name = device.get('title')

        # variables only for Playlist
        self.autoplay = 0


    def actions(self):
        """
        Return a list of actions for this item
        """
        return [ Action(_('Browse disc'), self.browse ) ]


    def browse(self):
        """
        Make a menu item for each file in the directory
        """
        play_items = []
        for track in self.info.list().get():
            play_items.append(AudioItem(track, self))

        # add all playable items to the playlist of the directory
        # to play one files after the other
        self.playlist = play_items

        # all items together
        items = []

        # random playlist (only active for audio)
        if 'audio' in config.directory.playlist.random and len(play_items) > 1:
            pl = Playlist(_('Random playlist'), play_items, self, random=True)
            pl.autoplay = True
            items += [ pl ]

        items += play_items

        # BEACON_FIXME
        # if hasattr(self.info, 'mixed'):
        #     d = DirItem(self.mountdir, self)
        #     d.name = _('Data files on disc')
        #     items.append(d)

        item_menu = Menu(self.name, items, type = self.display_type)
        self.pushmenu(item_menu)
