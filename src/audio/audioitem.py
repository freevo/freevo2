# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# audioitem - Item for mp3 and ogg files
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
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


import os
import re
import traceback

import config
import player

from item import MediaItem
from event import *


class AudioItem(MediaItem):
    """
    This is the common class to get information about audiofiles.
    """
    
    def __init__(self, url, parent, name=None, scan=True):
        MediaItem.__init__(self, 'audio', parent)

        self.set_url(url, info=scan)

        if name:
            self.name   = name

        self.start      = 0
        self.elapsed    = 0
        self.remain     = 0
        self.pause      = 0

        self.mplayer_options = ''
            
        try:
            self.length = int(self.info['length'])
        except:
            self.length = 0
            
        # Let's try to find if there is any image in the current directory
        # that could be used as a cover
        if self.filename and not self.image and not \
           (self.parent and self.parent.type == 'dir'):
            images = ()
            covers = ()
            files =()
            def image_filter(x):
                return re.match('.*(jpg|png)$', x, re.IGNORECASE)
            def cover_filter(x):
                return re.search(config.AUDIO_COVER_REGEXP, x, re.IGNORECASE)

            # Pick an image if it is the only image in this dir, or it matches
            # the configurable regexp
            dirname = os.path.dirname(self.filename)
            try:
                files = os.listdir(dirname)
            except OSError:
                print "oops, os.listdir() error"
                traceback.print_exc()
            images = filter(image_filter, files)
            image = None
            if len(images) == 1:
                image = os.path.join(dirname, images[0])
            elif len(images) > 1:
                covers = filter(cover_filter, images)
                if covers:
                    image = os.path.join(dirname, covers[0])
            self.image = image


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            if self.filename:
                return u'%s%s' % (os.stat(self.filename).st_ctime, Unicode(self.filename))
        if mode == 'advanced':
            # sort by track number
            try:
                return '%s %0.3i-%s' % (self['discs'],int(self['trackno']), Unicode(self.url))
            except ValueError:
                return '%s-%s' % (Unicode(self['trackno']), Unicode(self.url))
        return Unicode(self.url)


    def set_url(self, url, info=True):
        """
        Sets a new url to the item. Always use this function and not set 'url'
        directly because this functions also changes other attributes, like
        filename, mode and network_play
        """
        MediaItem.set_url(self, url, info)
        if url.startswith('cdda://'):
            self.network_play = False
            self.mimetype = 'cdda'


    def __getitem__(self, key):
        """
        return the specific attribute as string or an empty string
        """
        if key  == 'length' and self.length:
            # maybe the length was wrong
            if self.length < self.elapsed:
                self.length = self.elapsed
            return '%d:%02d' % (int(self.length / 60), int(self.length % 60))

        if key  == 'elapsed':
            return '%d:%02d' % (int(self.elapsed / 60), int(self.elapsed % 60))
            
        return MediaItem.__getitem__(self, key)

   
    # ----------------------------------------------------------------------------

    def actions(self):
        """
        return a list of possible actions on this item
        """
        return [ ( self.play, 'Play' ) ]


    def play(self, arg=None, menuw=None):
        """
        Start playing the item
        """
        self.parent.current_item = self
        self.elapsed = 0

        player.get_singleton().play(self)


    def stop(self, arg=None, menuw=None):
        """
        Stop the current playing
        """
        player.get_singleton().stop()
