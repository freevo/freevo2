# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# player.py - the Freevo video player
# -----------------------------------------------------------------------------
# $Id$
#
# This module provides the video player. It will use one of the registered
# player plugins to play the video item (e.g. video.mplayer)
#
# You can access the player by calling videoplayer()
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: ?
# Maintainer:    ?
#
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
# -----------------------------------------------------------------------------

__all__ = [ 'videoplayer' ]

# kaa imports
import kaa.popcorn
import kaa.notifier

# Freevo imports
import config

from event import *
from application import Application, STATUS_RUNNING, STATUS_STOPPING, \
	 STATUS_STOPPED, STATUS_IDLE, CAPABILITY_TOGGLE, CAPABILITY_PAUSE, \
	 CAPABILITY_FULLSCREEN

import logging
log = logging.getLogger('video')

_singleton = None

def videoplayer():
    """
    return the global video player object
    """
    global _singleton
    if _singleton == None:
        _singleton = VideoPlayer()
    return _singleton


class VideoPlayer(Application):
    """
    basic object to handle the different player
    """
    def __init__(self):
        capabilities = (CAPABILITY_PAUSE, CAPABILITY_FULLSCREEN)
        Application.__init__(self, 'videoplayer', 'video', capabilities)
        self.player = kaa.popcorn.Player()
        self.player.set_window(self.engine.get_window())
        self.player.signals['failed'].connect_weak(self._play_failed)


    def play(self, item, player=None):
        """
        play an item
        """
        # FIXME: handle starting something when self.player.is_playing()
        # if self.player and self.player.is_playing():
        #     return

        self.item = item

        # set the current item to the gui engine
        self.engine.set_item(self.item)
        self.status = STATUS_RUNNING

        self.player.open(self.item.url)
        self.player.signals['end'].connect_once(PLAY_END.post, self.item)
        self.player.signals['start'].connect_once(PLAY_START.post, self.item)

        if item.info.get('interlaced'):
            self.player.set_property('deinterlace', True)

        # FIXME: set more properties
        self.player.play()


    def _play_failed(self):
        """
        Playing this item failed.
        """
        log.error('playback failed for %s', self.item)
        # disconnect the signal handler with that item
        self.player.signals['end'].disconnect(PLAY_END.post, self.item)
        self.player.signals['start'].disconnect(PLAY_START.post, self.item)
        # We should handle it here with a messge or something like that. To
        # make playlist work, we just send start and stop. It's ugly but it
        # should work.
        PLAY_START.post(self.item)
        PLAY_END.post(self.item)


    def stop(self):
        """
        Stop playing.
        """
        # This function doesn't use the Application.stop() code here
        # because we stop and it is stopped when the child is dead.
        self.player.stop()
        self.status = STATUS_STOPPING


    def eventhandler(self, event):
        """
        React on some events or send them to the real player or the
        item belongig to the player
        """
        # FIXME: handle next player on PLAY_END when there was an error

        if event == STOP:
            # Stop the player and pass the event to the item
            self.stop()
            self.item.eventhandler(event)
            return True

        if event == PLAY_START:
            self.item.eventhandler(event)
            return True

        if event == PLAY_END:
            # Now the player has stopped (either we called self.stop() or the
            # player stopped by itself. So we need to set the application to
            # to stopped.
            self.status = STATUS_STOPPED
            self.item.eventhandler(event)
            if self.status == STATUS_STOPPED:
                self.status = STATUS_IDLE
            return True

        if event == PAUSE:
            self.player.pause()
            return True

        if event == PLAY:
            self.player.resume()
            return True

        if event == SEEK:
            self.player.seek(int(event.arg), kaa.popcorn.SEEK_RELATIVE)
            return True

        if event == VIDEO_TOGGLE_INTERLACE:
            interlaced = not self.player.get_property('deinterlace')
            self.item.info['interlaced'] = interlaced
            self.player.set_property('deinterlace', interlaced)
            return True
        
        # give it to the item
        return self.item.eventhandler(event)
