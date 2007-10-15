# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# audioitem - Item for mp3 and ogg files
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains an item used for audio files. It handles all actions
# possible for an audio item
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
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

__all__ = [ 'AudioItem' ]

# python imports
import os
import logging

# kaa imports
from kaa.strutils import str_to_unicode

# freevo imports
from freevo.ui.menu import MediaItem, Action
from freevo.ui.event import PLAY_END, STOP

# audio player
import player as audioplayer

# get logging object
log = logging.getLogger('audio')

class AudioItem(MediaItem):
    """
    This is the common class to get information about audiofiles.
    """
    type = 'audio'
    
    def __init__(self, url, parent):
        MediaItem.__init__(self, parent)
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
        return MediaItem.sort(self, mode)


    def set_url(self, url):
        """
        Sets a new url to the item. Always use this function and not set 'url'
        directly because this functions also changes other attributes, like
        filename, mode and network_play
        """
        MediaItem.set_url(self, url)
        if self.url.startswith('cdda://'):
            self.network_play = False


    def actions(self):
        """
        return a list of possible actions on this item
        """
        return [ Action('Play',  self.play) ]


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
        if event == STOP:
            self.user_stop = True
        if event == PLAY_END:
            if not self.user_stop:
                self['last_played'] = int(time.time())
                self.user_stop = False
        return MediaItem.eventhandler(self, event)
