# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# videoitem.py - Item for video objects
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2012 Dirk Meyer, et al.
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

__all__ = [ 'VideoItem' ]

# python imports
import logging
import time

# kaa imports
import kaa
try:
    import kaa.webmetadata as webmetadata
except ImportError:
    webmetadata = None

# freevo imports
from ... import core as freevo
from player import player as videoplayer

# get logging object
log = logging.getLogger('video')

class VideoItem(freevo.MediaItem):
    type = 'video'

    user_stop = False

    def __init__(self, url, parent):
        super(VideoItem, self).__init__(parent)
        self.player = str(freevo.config.video.player.default)
        self.set_url(url)

    def set_url(self, url):
        """
        Sets a new url to the item. Always use this function and not set 'url'
        directly because this functions also changes other attributes.
        """
        super(VideoItem, self).set_url(url)
        if self.get('series') and self.get('season') and self.get('episode') and self.get('title'):
            # FIXME: make this a configure option and fix sorting if season is >9
            self.name = '%s %dx%02d - %s' % (
                self.get('series'), self.get('season'), self.get('episode'), self.get('title'))

    @property
    def webmetadata(self):
        """
        Return webmetadata
        """
        if not webmetadata:
            return None
        if not hasattr(self, '_webmetadata'):
            self._webmetadata = webmetadata.parse(self.filename, self.metadata)
        return self._webmetadata

    @property
    def background(self):
        """
        Return background art
        """
        if not hasattr(self, '_background'):
            self._background = None
            if self.webmetadata and self.webmetadata.series.image:
                self._background = self.webmetadata.series.image
        return self._background

    @property
    def geometry(self):
        """
        Return width x height of the image or None
        """
        if self.get('width') and self.get('height'):
            return '%sx%s' % (self.get('width'), self.get('height'))
        return None

    @property
    def aspect(self):
        """
        Return aspect as string or None if unknown
        """
        if self.info.get('aspect'):
            aspect = str(self.info.get('aspect'))
            return aspect[:aspect.find(' ')].replace('/', ':')
        return None

    def actions(self):
        """
        return a list of possible actions on this item.
        """
        return [ freevo.Action(_('Play'), self.play) ]

    def play(self):
        """
        Play the item.
        """
        videoplayer.play(self)

    def stop(self):
        """
        stop playing
        """
        videoplayer.stop()

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
        super(VideoItem, self).eventhandler(event)
