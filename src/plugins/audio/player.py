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

# Freevo imports
from ... import core as freevo

# get logging object
log = logging.getLogger('audio')

class Player(freevo.Player):
    """
    Audio player object.
    """

    name = 'audioplayer'
    player = None

    def __init__(self):
        capabilities = (freevo.CAPABILITY_TOGGLE, freevo.CAPABILITY_PAUSE)
        super(Player, self).__init__('audio', capabilities)

    @kaa.coroutine()
    def play(self, item):
        """
        play an item
        """
        if not 'gstreamer' in kaa.candy.POSSIBLE_PLAYER:
            # FIXME: find a fallback player here
            freevo.Event(freevo.OSD_MESSAGE, _('Unsupported player: gstreamer')).post()
            yield False
        if not (yield super(Player, self).play(item, ['AUDIO'])):
            yield False
        log.info('start playing %s', self.item.filename)
        # Open media item and start playback
        self.player = self.widget.get_widget('player')
        self.player.uri = item.filename
        self.player.signals['finished'].connect_weak_once(self.PLAY_END.post, self.item)
        self.player.signals['progress'].connect_weak(self.set_elapsed)
        self.player.play()
        self.PLAY_START.post(self.item)
        yield True

    def do_stop(self):
        """
        Stop playing.
        """
        self.player.stop()

    def get_json(self, httpserver):
        """
        Return a dict with attributes about the application used by
        the provided httpserver to send to a remote controlling
        client.
        """
        properties = self.item.properties
        return { 'title': properties.title,
                 'artist': properties.artist,
                 'album': properties.album
               }

    def eventhandler(self, event):
        """
        React on some events or send them to the real player or the
        item belongig to the player
        """
        if super(Player, self).eventhandler(event):
            # Generic start/stop handling
            if event == freevo.PLAY_END and self.player:
                self.player = None
            return True
        if not self.player:
            # No player object and therefore, no playback control
            return self.item.eventhandler(event)
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
        if not self.player:
            yield False
        if self.player.state == kaa.candy.STATE_PLAYING:
            self.player.pause()
            # there is no feedback from kaa.candy if that worked. Just
            # wait half a second
            yield kaa.delay(0.5)
        self.free_resources()
        yield True

    @kaa.coroutine()
    def resume(self):
        """
        Resume playing the audio, at the position before.
        """
        if (yield self.get_resources('AUDIO')) == False:
            # That should not happen. But well, if it does, the player
            # is kind of dead now and the user has to restart it
            # itself
            log.error('unable to get AUDIO ressource')
            yield False
        self.player.resume()


# create singleton object
player = kaa.utils.Singleton(Player)

# create functions to use from the outside
play = player.play
stop = player.stop
