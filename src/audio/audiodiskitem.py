# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# audiodiskitem.py - Item for CD Audio Disks
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.30  2004/07/10 12:33:37  dischi
# header cleanup
#
# Revision 1.29  2004/01/25 14:55:05  dischi
# use overlay dir for covers
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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
# ----------------------------------------------------------------------- */


import config
import menu
import os

from item import Item
from audioitem import AudioItem
from playlist import Playlist
from directory import DirItem

class AudioDiskItem(Playlist):
    """
    class for handling audio disks
    """
    def __init__(self, disc_id, parent, devicename = None, display_type = None):

        Playlist.__init__(self, parent=parent)
        self.type = 'audiocd'
        self.media = None
        self.disc_id = disc_id
        self.devicename = devicename
        self.name = _('Unknown CD Album')
        
        # variables only for Playlist
        self.autoplay = 0

        # variables only for DirItem
        self.display_type = display_type

        cover = '%s/disc/metadata/%s.jpg' % (config.OVERLAY_DIR, disc_id)
        if os.path.isfile(cover):
            self.image = cover
            

    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.cwd, _('Browse disc') ) ]
        return items

    
    def cwd(self, arg=None, menuw=None):
        """
        make a menu item for each file in the directory
        """
        play_items = []
        number = len(self.info['tracks'])
        if hasattr(self.info, 'mixed'):
            number -= 1

        for i in range(0, number):
            title=self.info['tracks'][i]['title']
            item = AudioItem('cdda://%d' % (i+1), self, title, scan=False)

            # XXX FIXME: set also all the other infos here if AudioInfo
            # XXX will be based on mmpython
            #item.set_info('', self.name, title, i+1, self.disc_id[1], '')
            item.info = self.info['tracks'][i]
            item.length = item.info['length']
            if config.MPLAYER_ARGS.has_key('cd'):
                item.mplayer_options += (' ' + config.MPLAYER_ARGS['cd'])

            if self.devicename:
                item.mplayer_options += ' -cdrom-device %s' % self.devicename
            play_items.append(item)

        # add all playable items to the playlist of the directory
        # to play one files after the other
        self.playlist = play_items

        # all items together
        items = []

        # random playlist (only active for audio)
        if 'audio' in config.DIRECTORY_ADD_RANDOM_PLAYLIST and len(play_items) > 1:
            pl = Playlist(_('Random playlist'), play_items, self, random=True)
            pl.autoplay = True
            items += [ pl ]

        items += play_items

        if hasattr(self.info, 'mixed'):
            d = DirItem(self.media.mountdir, self)
            d.name = _('Data files on disc')
            items.append(d)
            
        self.play_items = play_items

        title = self.name
        if title[0] == '[' and title[-1] == ']':
            title = self.name[1:-1]

        item_menu = menu.Menu(title, items, item_types = self.display_type)
        if menuw:
            menuw.pushmenu(item_menu)

        return items
