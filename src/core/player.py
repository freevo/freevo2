# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# player.py - a generic Freevo player
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

__all__ = [ 'Player' ]

# python imports
import logging

# kaa imports
import kaa
import kaa.utils

# Freevo imports
import api as freevo

# get logging object
log = logging.getLogger('player')

class Player(freevo.Application):
    """
    player object.
    """

    def __init__(self, eventmap, capabilities=[]):
        """
        Init the Player object.
        """
        super(Player, self).__init__(eventmap, capabilities)
        self.PLAY_START = freevo.Event(freevo.PLAY_START, handler=self.eventhandler)
        self.PLAY_END = freevo.Event(freevo.PLAY_END, handler=self.eventhandler)
        self.menustack = None

    @kaa.coroutine()
    def play(self, item, resources):
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
        if (yield self.get_resources(*resources, force=True)) == False:
            log.error("Can't get resource %s", str(resources))
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
        self.context.playlist = self.playlist
        self.item.elapsed_secs = 0
        self.status = freevo.STATUS_RUNNING
        # update GUI
        yield kaa.NotFinished
        yield True

    def set_elapsed(self, pos):
        """
        Callback for elapsed time changes.
        """
        if self.item.elapsed_secs != round(pos):
            self.item.elapsed_secs = round(pos)
            self.context.sync()

    def do_stop(self):
        """
        Stop playing. Override this function in the actual player to
        do the real stop.
        """
        pass

    def stop(self):
        """
        Stop playing.
        """
        if self.status != freevo.STATUS_RUNNING:
            # already stopped
            return False
        self.do_stop()
        self.status = freevo.STATUS_STOPPING
        return True

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
        if event == freevo.PLAY_END and event.arg == self.item:
            # Now the player has stopped (either we called self.stop() or the
            # player stopped by itself. So we need to set the application to
            # to stopped.
            self.status = freevo.STATUS_STOPPED
            self.item.eventhandler(event)
            if self.status == freevo.STATUS_STOPPED:
                self.status = freevo.STATUS_IDLE
                if self.menustack:
                    self.menustack = None
                    self.eventmap = self.orig_eventmap
            return True
        if event == freevo.MENU:
            # Show a menu during playback
            items = []
            for p in freevo.ItemPlugin.plugins(self.item.type):
                items += p.actions_playback(self.item, self)
            if items:
                self.menustack = freevo.MenuStack()
                self.menustack.pushmenu(freevo.Menu(_('Menu'), items))
                self.context.menu = self.menustack.current
                self.widget.osd.show('menu')
                self.orig_eventmap = self.eventmap
                self.eventmap = 'menu'
            return True
        if self.menustack:
            if self.menustack.eventhandler(event):
                if self.context.menu != self.menustack.current:
                    self.context.previous = self.context.menu
                    self.context.next = self.menustack.current
                    self.context.menu = self.menustack.current
                # set item to currently selected (or None for an empty menu)
                self.context.item = None
                if self.menustack.current.selected:
                    self.context.item = self.menustack.current.selected.properties
                return True
            elif event == freevo.MENU_BACK_ONE_MENU:
                self.menustack = None
                self.widget.osd.hide('menu')
                self.eventmap = self.orig_eventmap
                return True
        return False
