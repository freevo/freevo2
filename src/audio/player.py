# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# player.py - the Freevo audio player
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
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

__all__ = [ 'audioplayer' ]

# python imports
import logging

# kaa imports
import kaa.popcorn
import kaa.notifier

# Freevo imports
import config

from event import *
from application import Application, STATUS_RUNNING, STATUS_STOPPING, \
	 STATUS_STOPPED, STATUS_IDLE, CAPABILITY_TOGGLE, CAPABILITY_PAUSE, \
	 CAPABILITY_FULLSCREEN

# get logging object
log = logging.getLogger('audio')

_singleton = None

def audioplayer():
    """
    Return the global audio player object
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
    Audio player object.
    """
    def __init__(self):
        capabilities = (CAPABILITY_TOGGLE, CAPABILITY_PAUSE)
        Application.__init__(self, 'audioplayer', 'audio', capabilities)
        self.player = kaa.popcorn.Player()
        self.player.signals['failed'].connect_weak(self._play_failed)
        self.elapsed_timer = kaa.notifier.WeakTimer(self.elapsed)


    def play(self, item, player=None):
        """
        play an item
        """
        if not self.status in (STATUS_IDLE, STATUS_STOPPED):
            # Already running, stop the current player by sending a STOP
            # event. The event will also get to the playlist behind the
            # current item and the whole list will be stopped.
            Event(STOP, handler=self.eventhandler).post()
            # Now connect to our own 'stop' signal once to repeat this current
            # function call without the player playing
            self.signals['stop'].connect_once(self.play, item)
            return True

        if not kaa.notifier.running:
            # Freevo is in shutdown mode, do not start a new player, the old
            # only stopped because of the shutdown.
            return False

        # Try to get AUDIO resource. The ressouce will be freed by the system
        # when the application switches to STATUS_STOPPED or STATUS_IDLE.
        blocked = self.get_resources('AUDIO')
        if 'AUDIO' in blocked:
            # Something has the audio resource blocked, stop it
            Event(STOP, handler=blocked['AUDIO'].eventhandler).post()
            # Now connect to the 'stop' signal once to repeat this current
            # function call without the player playing
            blocked['AUDIO'].signals['stop'].connect_once(self.play, item)
            return True

        # store item and playlist
        self.item = item
        self.playlist = self.item.get_playlist()
        if self.playlist:
            self.playlist.select(self.item)

        # Calculate some new values
        if not self.item.length:
            self.item.remain = 0
        else:
            self.item.remain = self.item.length - self.item.elapsed

        # set the current item to the gui engine
        self.engine.set_item(self.item)
        self.status = STATUS_RUNNING

        self.player.open(self.item.url)
        self.player.signals['end'].connect_once(PLAY_END.post, self.item)
        self.player.signals['start'].connect_once(PLAY_START.post, self.item)
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


    @kaa.notifier.yield_execution()
    def pause(self):
        """
        Pause Playback. Return False if already paused.
        """
        # FIXME: make sure this function is not called twice
        if not self.status == STATUS_RUNNING:
            yield False
        if self.player.get_state() == kaa.popcorn.STATE_PAUSED:
            yield None
        # FIXME: what happens if we send pause() the same time the file
        # is finished? This would create a race condition.
        self.player.pause()
        yield kaa.notifier.YieldCallback(self.player.signals['pause'])
        self.free_resources()


    @kaa.notifier.yield_execution()
    def resume(self):
        """
        Resume Playback. Return False if already resumed.
        """
        # FIXME: make sure this function is not called twice
        if not self.status == STATUS_RUNNING:
            yield False
        if self.player.get_state() == kaa.popcorn.STATE_PLAYING:
            yield False
        if self.get_resources('AUDIO'):
            # FIXME: what to do in this case?
            log.error('unable to get AUDIO ressource')
            yield False
        self.player.resume()
        yield kaa.notifier.YieldCallback(self.player.signals['play'])


    def elapsed(self):
        """
        Callback for elapsed time changes.
        """
        self.item.elapsed = round(self.player.get_position())
        # Calculate some new values
        if not self.item.length:
            self.item.remain = 0
        else:
            self.item.remain = self.item.length - self.item.elapsed
        # redraw
        self.engine.update()


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
            self.status = STATUS_STOPPED
            self.elapsed_timer.stop()
            self.item.eventhandler(event)
            if self.status == STATUS_STOPPED:
                self.status = STATUS_IDLE
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
