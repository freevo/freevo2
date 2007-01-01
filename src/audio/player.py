# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# player.py - the Freevo audio player
# -----------------------------------------------------------------------------
# $Id$
#
# This module provides the audio player. It will use one of the registered
# player plugins to play the audio item (e.g. audio.mplayer)
#
# You can access the player by calling audioplayer()
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

__all__ = [ 'audioplayer' ]

# kaa imports
import kaa.popcorn
import kaa.notifier

# Freevo imports
import config
import gui
import gui.areas

from event import *
from application import Application

import logging
log = logging.getLogger('audio')

_singleton = None

def audioplayer():
    """
    return the global audio player object
    """
    global _singleton
    if _singleton == None:
        _singleton = AudioPlayer()
    return _singleton


# Visualization events
AUDIO_VISUAL_SHOW = Event('AUDIO_VISUAL_SHOW')
AUDIO_VISUAL_HIDE = Event('AUDIO_VISUAL_HIDE')


class AudioPlayer(Application):
    """
    basic object to handle the different player
    """
    def __init__(self):
        Application.__init__(self, 'audioplayer', 'audio', False, True)
        self.player = kaa.popcorn.Player()
        self.player.signals['failed'].connect_weak(self._play_failed)
        self.running    = False
        self.bg_playing = False
        self.elapsed_timer = kaa.notifier.WeakTimer(self.elapsed)
        
        # register player to the skin
        areas = ('screen', 'title', 'view', 'info')
        self.draw_engine = gui.areas.Handler('player', areas)


    def play(self, item, player=None):
        """
        play an item
        """
        # FIXME: handle starting something when self.player.is_playing()
        # if self.player and self.player.is_playing():
        #     return

        self.item = item
        self.running = True

        if self.bg_playing:
            log.info('start new background playing')
        else:
            self.show()

        self.player.open(self.item.url)
        self.player.signals['end'].connect_once(PLAY_END.post, self.item)
        self.player.signals['start'].connect_once(PLAY_START.post, self.item)
        self.player.play()
        self.refresh()


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
        self.running = False


    def show(self):
        """
        show the player gui
        """
        Application.show(self)
        self.bg_playing = False
        self.refresh()
        self.draw_engine.show(config.GUI_FADE_STEPS)

        # post event for showing visualizations
        # FIXME: maybe this is a Signal
        AUDIO_VISUAL_SHOW.post()


    def hide(self):
        """
        hide the player gui
        """
        Application.hide(self)
        self.draw_engine.hide(config.GUI_FADE_STEPS)
        # DOES NOT WORK
        # if self.running:
        #   self.bg_playing = True

        # post event for hiding visualizations
        # FIXME: maybe this is a Signal
        AUDIO_VISUAL_HIDE.post()


    def elapsed(self):
        """
        Callback for elapsed time changes.
        """
        self.item.elapsed = round(self.player.get_position())
        self.refresh()


    def refresh(self):
        """
        update the screen
        """
        if not self.visible or not self.running:
            return
        # Calculate some new values
        if not self.item.length:
            self.item.remain = 0
        else:
            self.item.remain = self.item.length - self.item.elapsed
        # redraw
        self.draw_engine.draw(self.item)


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
            self.elapsed_timer.start(0.2)
            self.item.eventhandler(event)
            return True

        if event == PLAY_END:
            # Now the player has stopped (either we called self.stop() or the
            # player stopped by itself. So we need to set the application to
            # to stopped.
            self.stopped()
            self.elapsed_timer.stop()
            self.item.eventhandler(event)
            return True

        if event == PAUSE:
            self.player.pause()
            self.elapsed_timer.stop()
            return True

        if event == PLAY:
            self.player.resume()
            self.elapsed_timer.start(0.2)
            return True

        if event == SEEK:
            self.player.seek(int(event.arg), kaa.popcorn.SEEK_RELATIVE)
            return True

        # give it to the item
        return self.item.eventhandler(event)
