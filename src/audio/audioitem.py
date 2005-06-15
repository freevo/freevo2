# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# audioitem - Item for mp3 and ogg files
# -----------------------------------------------------------------------
# $Id$
#
# This file contains an item used for audio files. It handles all actions
# possible for an audio item (right now only 'play')
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.67  2005/06/15 20:43:39  dischi
# adjust to new menu code
#
# Revision 1.66  2005/06/12 18:49:53  dischi
# adjust to new menu code
#
# Revision 1.65  2005/04/10 17:49:46  dischi
# switch to new mediainfo module, remove old code now in mediadb
#
# Revision 1.64  2004/11/20 18:23:00  dischi
# use python logger module for debug
#
# Revision 1.63  2004/09/13 19:35:35  dischi
# replace player.get_singleton() with audioplayer()
#
# Revision 1.62  2004/09/10 19:50:06  outlyer
# Copy fix from 1.5.1 to HEAD branch.
#
# Revision 1.61  2004/08/27 14:24:25  dischi
# AudioItem is now based on MediaItem
#
# Revision 1.60  2004/08/01 10:42:51  dischi
# make the player an "Application"
#
# Revision 1.59  2004/07/26 18:10:16  dischi
# move global event handling to eventhandler.py
#
# Revision 1.58  2004/07/21 16:14:42  outlyer
# Typo. I'll put the fix into the stable branch in a second.
#
# Revision 1.57  2004/07/17 08:18:55  dischi
# unicode fixes
#
# Revision 1.56  2004/07/10 13:36:07  outlyer
# Handle the situation where track number can't be converted into an int()
#
# Revision 1.55  2004/07/10 12:33:37  dischi
# header cleanup
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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

__all__ = [ 'AudioItem' ]

# Python imports
import os
import re

# Freevo imports
import config
from menu import MediaItem, Action
from event import *

from player import *

import logging
log = logging.getLogger('audio')

class AudioItem(MediaItem):
    """
    This is the common class to get information about audiofiles.
    """
    def __init__(self, url, parent):
        MediaItem.__init__(self, parent, type='audio')
        self.set_url(url)
        self.start      = 0
        self.elapsed    = 0
        self.remain     = 0
        self.pause      = 0
        self.mplayer_options = ''
        self.length     = 0
            

    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            if self.filename:
                return u'%s%s' % (os.stat(self.filename).st_ctime,
                                  Unicode(self.filename))
        if mode == 'advanced':
            # sort by track number
            try:
                return '%s %0.3i-%s' % (self['discs'], int(self['trackno']),
                                        Unicode(self.url))
            except ValueError:
                return '%s-%s' % (Unicode(self['trackno']), Unicode(self.url))
        return Unicode(self.url)


    def set_url(self, url):
        """
        Sets a new url to the item. Always use this function and not set 'url'
        directly because this functions also changes other attributes, like
        filename, mode and network_play
        """
        MediaItem.set_url(self, url)
        if self.url.startswith('cdda://'):
            self.network_play = False
            self.mimetype = 'cdda'


    def __init_info__(self):
        MediaItem.__init_info__(self)
        try:
            self.length = int(self.info['length'])
        except:
            self.length = 0

        
    def __getitem__(self, key):
        """
        return the specific attribute as string or an empty string
        """
        if key  == 'length':
            if self.length:
                # maybe the length was wrong
                if self.length < self.elapsed:
                    self.length = self.elapsed
                return '%d:%02d' % (int(self.length / 60), \
                                    int(self.length % 60))

        if key  == 'elapsed':
            return '%d:%02d' % (int(self.elapsed / 60), int(self.elapsed % 60))
            
        return MediaItem.__getitem__(self, key)

   
    def actions(self):
        """
        return a list of possible actions on this item
        """
        return [ Action('Play',  self.play) ]


    def play(self):
        """
        Start playing the item
        """
        self.parent.current_item = self
        self.elapsed = 0
        audioplayer().play(self)


    def stop(self):
        """
        Stop the current playing
        """
        audioplayer().stop()
