# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# player.py - a generic player for the games
# -----------------------------------------------------------------------------
# $Id$
#
# This player starts a emulator player. This class handles all the events
# from the freevo system and sends them to the different players.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Mathias Weber <mweb@gmx.ch>
# Maintainer:    Mathias Weber <mweb@gmx.ch>
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

__all__ = [ 'play', 'stop']

# python imports
import logging

# kaa imports
import kaa
import kaa.utils

# freevo imports
from freevo.ui.event import *
from freevo.ui.application import Application, STATUS_RUNNING, \
        STATUS_STOPPING, STATUS_STOPPED, STATUS_IDLE, CAPABILITY_FULLSCREEN

log  = logging.getLogger('games')

class GamesPlayer(Application):
    """
    Games player object.
    """
    def __init__(self):
        capabilities = (CAPABILITY_FULLSCREEN, )
        Application.__init__(self, 'gamesplayer', 'games', capabilities)
        self.player = None


    def play(self, item, player):
        """
        play an item
        """
        if player == None:
            return False
        self.player = player
        retry = kaa.Callback(self.play, item, player)
        if not self.status in (STATUS_IDLE, STATUS_STOPPED):
            # Already running, stop the current player by sending a STOP
            # event. The event will also get to the playlist behind the
            # current item and the whole list will be stopped.
            Event(STOP, handler=self.eventhandler).post()
            # Now connect to our own 'stop' signal once to repeat this current
            # function call without the player playing
            self.signals['stop'].connect_once(self.play, item)
            return True

        if not kaa.main.is_running():
            # Freevo is in shutdown mode, do not start a new player, the old
            # only stopped because of the shutdown.
            return False

        # Try to get VIDEO and AUDIO resources. The ressouces will be freed
        # by the system when the application switches to STATUS_STOPPED or
        # STATUS_IDLE.
        blocked = self.get_resources('AUDIO', 'VIDEO', 'JOYSTICK', force=True)
        if not blocked.is_finished():
            blocked.connect(retry)
            return True
        if blocked == False:
            log.error("Can't get resource AUDIO, VIDEO, JOYSTICK")
            return False

        # store item
        self.item = item
        self.status = STATUS_RUNNING

        self.player.open(self.item)
        self.player.signals['failed'].connect_once(self._play_failed)
        self.player.signals['end'].connect_once(PLAY_END.post, self.item)
        self.player.signals['start'].connect_once(PLAY_START.post, self.item)
        self.player.play()


    def _play_failed(self):
        """
        Playing this item failed.
        """
        log.error('playback failed for %s', self.item)


    def stop(self):
        """
        Stop playing.
        """
        if self.get_status() != STATUS_RUNNING:
            return True
        self.player.stop()
        self.status = STATUS_STOPPING


    def eventhandler(self, event):
        """
        React on events and do the right command with the game.
        """
        if event == STOP:
            self.stop()
            if not self.player.is_running():
                self.item.eventhandler(event)
                self.status = STATUS_IDLE
            return True

        elif event == PLAY_END:
            self.stop()
            self.show()
            self.item.eventhandler(event)
            return True

        return self.item.eventhandler(event)


player = kaa.utils.Singleton(GamesPlayer)
play = player.play
stop = player.stop

