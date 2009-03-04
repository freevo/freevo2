# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# item.py - AudioItem and AudioDiskItem
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains an item used for audio files. It handles all actions
# possible for an audio item
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2009 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
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

__all__ = [ 'AudioItem', 'AudioDiskItem' ]

# python imports
import logging
import time

# kaa imports
import kaa

# freevo imports
from ... import core as freevo

# audio player
import player as audioplayer

# get logging object
log = logging.getLogger('audio')


class AudioItem(freevo.MediaItem):
    """
    This is the common class to get information about audiofiles.
    """
    type = 'audio'

    def __init__(self, url, parent):
        super(AudioItem, self).__init__(parent)
        self.user_stop = False
        self.set_url(url)

    def sort(self, mode='name'):
        """
        Returns the string how to sort this item
        """
        if mode in ('name', 'smart'):
            try:
                track = int(self.info.get('trackno'))
            except (ValueError, KeyError, TypeError):
                track = 0
            return u'%20d %s' % (track, self.name.lower())
        return super(AudioItem, self).sort(mode)

    def actions(self):
        """
        return a list of possible actions on this item
        """
        return [ freevo.Action('Play',  self.play) ]

    def play(self):
        """
        Start playing the item
        """
        self.elapsed = 0
        audioplayer.play(self)

    def stop(self):
        """
        Stop the current playing
        """
        audioplayer.stop()

    def eventhandler(self, event):
        """
        eventhandler for this item
        """
        if event == freevo.STOP:
            self.user_stop = True
        if event == freevo.PLAY_END:
            if not self.user_stop:
                self['last_played'] = int(time.time())
                self.user_stop = False
        return super(AudioItem, self).eventhandler(event)


class AudioDiskItem(freevo.Playlist):
    """
    Class for handling audio disks.
    """
    def __init__(self, device, parent):
        super(AudioDiskItem, self).__init__(parent=parent, type='audio')
        self.type = 'audiocd'
        self.info = device
        self.name = device.get('title')
        # variables only for Playlist
        self.autoplay = 0

    def actions(self):
        """
        Return a list of actions for this item
        """
        return [ freevo.Action(_('Browse disc'), self.browse ) ]

    @kaa.coroutine()
    def browse(self):
        """
        Make a menu item for each file in the directory
        """
        play_items = []
        for track in (yield self.info.list()):
            play_items.append(AudioItem(track, self))
        # add all playable items to the playlist of the directory
        # to play one files after the other
        self.set_playlist(play_items)
        # all items together
        items = []
        # random playlist (only active for audio)
        if freevo.config.directory.add_random_playlist and len(play_items) > 1:
            pl = freevo.Playlist(_('Random playlist'), play_items, self, random=True)
            pl.autoplay = True
            items += [ pl ]
        items += play_items
        # BEACON_FIXME
        # if hasattr(self.info, 'mixed'):
        #     d = freevo.Directory(self.mountdir, self)
        #     d.name = _('Data files on disc')
        #     items.append(d)
        item_menu = freevo.Menu(self.name, items, type = 'audio')
        self.menustack.pushmenu(item_menu)
