#if 0 /*
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
# Revision 1.24  2003/11/08 12:58:41  dischi
# better support for mixed discs
#
# Revision 1.23  2003/11/05 21:18:42  dischi
# mixed disc support (needs mmpython cvs)
#
# Revision 1.22  2003/09/20 09:44:23  dischi
# cleanup
#
# Revision 1.21  2003/09/13 10:08:21  dischi
# i18n support
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
#endif


import config
import menu
import os

from item import Item
from audioitem import AudioItem
from playlist import Playlist, RandomPlaylist
from directory import DirItem

class AudioDiskItem(Playlist):
    """
    class for handling audio disks
    """
    def __init__(self, disc_id, parent, devicename = None, display_type = None):

        Item.__init__(self, parent)
        self.type = 'audiocd'
        self.media = None
        self.disc_id = disc_id
        self.devicename = devicename
        self.name = _('Unknown CD Album')
        
        # variables only for Playlist
        self.current_item = 0
        self.playlist = []
        self.autoplay = 0

        # variables only for DirItem
        self.display_type = display_type

        # set directory variables to default
        all_variables = ('DIRECTORY_AUTOPLAY_SINGLE_ITEM',
                         'AUDIO_RANDOM_PLAYLIST')
        for v in all_variables:
            setattr(self, v, eval('config.%s' % v))

        cover = '%s/mmpython/disc/%s.jpg' % (config.FREEVO_CACHEDIR, disc_id)
        if os.path.isfile(cover):
            self.image = cover
            

    def copy(self, obj):
        """
        Special copy value DirItem
        """
        Playlist.copy(self, obj)
        if obj.type == 'audiocd':
            self.dir          = obj.dir
            self.display_type = obj.display_type
            

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
        if len(play_items) > 1 and config.AUDIO_RANDOM_PLAYLIST == 1:
            pl = Playlist(play_items, self)
            pl.randomize()
            pl.autoplay = 1
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
