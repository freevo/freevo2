# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# item.py - AudioItem
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

__all__ = [ 'AudioItem' ]

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
            return u'%20d %s' % (track, kaa.py3_str(self.name.lower()))
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
