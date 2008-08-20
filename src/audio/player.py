# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# player.py - the Freevo audio player
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
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

__all__ = [ 'play', 'stop' ]

# python imports
import logging

# kaa imports
import kaa
import kaa.utils
import kaa.popcorn

# Freevo imports
from freevo.ui.event import *
from freevo.ui.application import Application, STATUS_RUNNING, STATUS_STOPPING, \
     STATUS_STOPPED, STATUS_IDLE, CAPABILITY_TOGGLE, CAPABILITY_PAUSE, \
     CAPABILITY_FULLSCREEN

# get logging object
log = logging.getLogger('audio')

class Player(Application):
    """
    Audio player object.
    """

    name = 'audioplayer'

    def __init__(self):
        capabilities = (CAPABILITY_TOGGLE, CAPABILITY_PAUSE)
        Application.__init__(self, 'audio', capabilities)
        self.player = kaa.popcorn.Player()
        self.elapsed_timer = kaa.WeakTimer(self.elapsed)


    @kaa.coroutine()
    def play(self, item):
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
            yield kaa.inprogress(self.signals['stop'])
            if not self.status in (STATUS_IDLE, STATUS_STOPPED):
                log.error('unable to stop current audio playback')
                yield False
        if not kaa.main.is_running():
            # Freevo is in shutdown mode, do not start a new player, the old
            # only stopped because of the shutdown.
            yield False

        # Try to get AUDIO resource. The ressouce will be freed by the system
        # when the application switches to STATUS_STOPPED or STATUS_IDLE.
        if (yield self.get_resources('AUDIO', force=True)) == False:
            log.error("Can't get Audio resource.")
            yield False

        # Store item and playlist. We need to keep the playlist object
        # here to make sure it is not deleted when player is running in
        # the background.
        self.item = item
        self.playlist = self.item.get_playlist()
        if self.playlist:
            self.playlist.select(self.item)

        # Set the current item to the gui engine
        self.gui_context.item = self.item.properties
        self.gui_context.menu = self.playlist
        self.status = STATUS_RUNNING

        # Open media item and start playback
        play_start = Event(PLAY_START, handler=self.eventhandler)
        play_end = Event(PLAY_END, handler=self.eventhandler)
        self.player.signals['end'].connect_once(play_end.post, self.item)
        try:
            yield self.player.open(self.item.url)
            yield self.player.play()
            play_start.post(self.item)
        except kaa.popcorn.PlayerError, e:
            self.player.signals['end'].disconnect(play_end.post, self.item)
            log.exception('video playback failed')
            # We should handle it here with a messge or something like that. To
            # make playlist work, we just send start and stop. It's ugly but it
            # should work.
            play_start.post(self.item)
            play_end.post(self.item)
        yield True


    def stop(self):
        """
        Stop playing.
        """
        if self.status != STATUS_RUNNING:
            return True
        self.player.stop()
        self.status = STATUS_STOPPING


    def elapsed(self):
        """
        Callback for elapsed time changes.
        """
        self.item.elapsed = round(self.player.position)
        self.gui_context.sync()


    def eventhandler(self, event):
        """
        React on some events or send them to the real player or the
        item belongig to the player
        """
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

        if event in (PAUSE, PLAY):
            if self.player.get_state() == kaa.popcorn.STATE_PLAYING:
                self.suspend()
                return True
            if self.player.get_state() == kaa.popcorn.STATE_PAUSED:
                self.resume()
                return True
            return False

        if event == SEEK:
            self.player.seek(int(event.arg), kaa.popcorn.SEEK_RELATIVE)
            return True

        return self.item.eventhandler(event)


    def can_suspend(self):
        """
        Return true since the application can be suspended.
        """
        return True

    @kaa.coroutine()
    def suspend(self):
        """
        Release the audio resource that others can use it.
        """
        # FIXME: make sure this function is not called twice
        if not self.status == STATUS_RUNNING:
            yield False
        if self.player.get_state() == kaa.popcorn.STATE_PAUSED:
            yield None
        # FIXME: what happens if we send pause() the same time the file
        # is finished? This would create a race condition.
        self.player.pause()
        yield kaa.inprogress(self.player.signals['pause'])
        self.free_resources()


    @kaa.coroutine()
    def resume(self):
        """
        Resume playing the audio, at the position before.
        """
        # FIXME: make sure this function is not called twice
        if not self.status == STATUS_RUNNING:
            yield False
        if self.player.get_state() == kaa.popcorn.STATE_PLAYING:
            yield False
        blocked = yield self.get_resources('AUDIO')
        if blocked == False:
            # FIXME: what to do in this case?
            log.error('unable to get AUDIO ressource')
            yield False
        self.player.resume()
        yield kaa.inprogress(self.player.signals['play'])


# create singleton object
player = kaa.utils.Singleton(Player)

# create functions to use from the outside
play = player.play
stop = player.stop
