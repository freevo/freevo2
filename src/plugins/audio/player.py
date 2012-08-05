# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# player.py - the Freevo audio player
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2012 Dirk Meyer, et al.
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
from ... import core as freevo

# get logging object
log = logging.getLogger('audio')

class Player(freevo.Application):
    """
    Audio player object.
    """

    name = 'audioplayer'
    player = None

    def __init__(self):
        capabilities = (freevo.CAPABILITY_TOGGLE, freevo.CAPABILITY_PAUSE)
        super(Player, self).__init__('audio', capabilities)
        self.PLAY_START = freevo.Event(freevo.PLAY_START, handler=self.eventhandler)
        self.PLAY_END = freevo.Event(freevo.PLAY_END, handler=self.eventhandler)

    @kaa.coroutine()
    def play(self, item):
        """
        play an item
        """
        if not self.status in (freevo.STATUS_IDLE, freevo.STATUS_STOPPED):
            # Already running, stop the current player by sending a STOP
            # event. The event will also get to the playlist behind the
            # current item and the whole list will be stopped.
            freevo.Event(freevo.STOP, handler=self.eventhandler).post()
            # Now connect to our own 'stop' signal once to repeat this current
            # function call without the player playing
            yield kaa.inprogress(self.signals['stop'])
            if not self.status in (freevo.STATUS_IDLE, freevo.STATUS_STOPPED):
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
        self.playlist = self.item.playlist
        if self.playlist:
            self.playlist.select(self.item)
        # Set the current item to the gui engine
        self.context.item = self.item.properties
        self.context.menu = self.playlist
        self.item.elapsed_secs = 0
        self.status = freevo.STATUS_RUNNING
        # update GUI
        yield kaa.NotFinished
        # Open media item and start playback
        self.player = self.widget.get_widget('player')
        self.player.url = item.filename
        self.player.signals['finished'].connect_weak_once(self.PLAY_END.post, self.item)
        self.player.signals['progress'].connect_weak(self.set_elapsed)
        self.player.play()
        self.PLAY_START.post(self.item)
        yield True

    def stop(self):
        """
        Stop playing.
        """
        if self.status != freevo.STATUS_RUNNING:
            return True
        self.player.stop()
        self.status = freevo.STATUS_STOPPING

    def set_elapsed(self, pos):
        """
        Callback for elapsed time changes.
        """
        if self.item.elapsed_secs != round(pos):
            self.item.elapsed_secs = round(pos)
            self.context.sync()

    def eventhandler(self, event):
        """
        React on some events or send them to the real player or the
        item belongig to the player
        """
        if event == freevo.STOP and self.status == freevo.STATUS_RUNNING:
            # Stop the player and pass the event to the item
            self.stop()
            self.item.eventhandler(event)
            return True
        if event == freevo.PLAY_START:
            self.item.eventhandler(event)
            return True
        if event == freevo.PLAY_END:
            # Now the player has stopped (either we called self.stop() or the
            # player stopped by itself. So we need to set the application to
            # to stopped.
            self.status = freevo.STATUS_STOPPED
            self.item.eventhandler(event)
            if self.status == freevo.STATUS_STOPPED:
                self.status = freevo.STATUS_IDLE
            return True
        if self.player:
            # player control makes only sense if the player is still running
            if event in (freevo.PAUSE, freevo.PLAY):
                if self.player.state == kaa.candy.STATE_PLAYING:
                    self.player.pause()
                    return True
                if self.player.state == kaa.candy.STATE_PAUSED:
                    self.player.resume()
                    return True
                return False
            if event == freevo.SEEK:
                self.player.seek(int(event.arg), kaa.candy.SEEK_RELATIVE)
                self.player.seek(int(event.arg), kaa.popcorn.SEEK_RELATIVE)
                return True
        return self.item.eventhandler(event)

    def can_suspend(self):
        """
        Return true since the application can be suspended.
        """
        return False

    # @kaa.coroutine()
    # def suspend(self):
    #     """
    #     Release the audio resource that others can use it.
    #     """
    #     # FIXME: make sure this function is not called twice
    #     if not self.status == freevo.STATUS_RUNNING:
    #         yield False
    #     if self.player.state == kaa.popcorn.STATE_PAUSED:
    #         yield None
    #     # FIXME: what happens if we send pause() the same time the file
    #     # is finished? This would create a race condition.
    #     self.player.pause()
    #     yield kaa.inprogress(self.player.signals['pause'])
    #     self.free_resources()

    # @kaa.coroutine()
    # def resume(self):
    #     """
    #     Resume playing the audio, at the position before.
    #     """
    #     # FIXME: make sure this function is not called twice
    #     if not self.status == freevo.STATUS_RUNNING:
    #         yield False
    #     if self.player.state == kaa.popcorn.STATE_PLAYING:
    #         yield False
    #     blocked = yield self.get_resources('AUDIO')
    #     if blocked == False:
    #         # FIXME: what to do in this case?
    #         log.error('unable to get AUDIO ressource')
    #         yield False
    #     self.player.resume()
    #     yield kaa.inprogress(self.player.signals['play'])


# create singleton object
player = kaa.utils.Singleton(Player)

# create functions to use from the outside
play = player.play
stop = player.stop
