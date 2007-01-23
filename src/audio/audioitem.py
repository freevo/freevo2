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
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al. 
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
# ----------------------------------------------------------------------- */

__all__ = [ 'AudioItem' ]

# Python imports
import os
import re

# kaa imports
from kaa.strutils import str_to_unicode

# Freevo imports
import config
from menu import MediaItem, Action
from event import *

import player as audioplayer

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
        try:
            self.length = int(self.info['length'])
        except:
            self.length = 0
            

    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            if self.filename:
                return u'%s%s' % (os.stat(self.filename).st_ctime,
                                  str_to_unicode(self.filename))
        if mode == 'advanced':
            # sort by track number
            try:
                return '%s %0.3i-%s' % (self['discs'], int(self['trackno']),
                                        str_to_unicode(self.url))
            except ValueError:
                return '%s-%s' % (unicode(self['trackno']), str_to_unicode(self.url))
        return str_to_unicode(self.url)


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
        self.elapsed = 0
        audioplayer.play(self)


    def stop(self):
        """
        Stop the current playing
        """
        audioplayer.stop()
