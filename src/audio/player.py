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
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: ?
# Maintainer:    ?
#
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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

# Freevo imports
import config
import gui
import gui.areas
import plugin
import eventhandler

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
        self.player     = None
        self.running    = False
        self.bg_playing = False

        # register player to the skin
        areas = ('screen', 'title', 'view', 'info')
        self.draw_engine = gui.areas.Handler('player', areas)


    def play(self, item, player=None):
        """
        play an item
        """
        self.item    = item
        if self.player and self.player.is_playing():
            log.info('stop playing')
            self.stop()

        self.item = item
        
        if player:
            self.player = player
        else:
            self.possible_player = []
            for p in plugin.getbyname(plugin.AUDIO_PLAYER, True):
                rating = p.rate(self.item) * 10
                if config.AUDIO_PREFERED_PLAYER == p.name:
                    rating += 1
                if hasattr(self.item, 'force_player') and \
                       p.name == self.item.force_player:
                    rating += 100
                self.possible_player.append((rating, p))
            self.possible_player.sort(lambda l, o: -cmp(l[0], o[0]))
            self.player = self.possible_player[0][1]
        
        self.running = True

        if self.bg_playing:
            log.info('start new background playing')
        else:
            self.show()

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        error = self.player.play(self.item, self)
        if error:
            self.running = False
            self.item.eventhandler(PLAY_END)
            
        else:
            self.refresh()


    def try_next_player(self):
        """
        try next possible player because the last one didn't work
        """
        self.stop()
        log.info('error, try next player')
        player = None
        next   = False
        for r, p in self.possible_player:
            if next:
                player = p
                break
            if p == self.player:
                next = True

        if player:
            self.play(self.item, player=player)
            return 1
        log.info('no more players found')
        return 0

        
    def stop(self):
        """
        stop playing
        """
        Application.stop(self)
        if self.player:
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
        eventhandler.post(AUDIO_VISUAL_SHOW)


    def hide(self):
        """
        hide the player gui
        """
        Application.hide(self)
        self.draw_engine.hide(config.GUI_FADE_STEPS)
        if self.running:
            self.bg_playing = True

        # post event for hiding visualizations
        eventhandler.post(AUDIO_VISUAL_HIDE)
            

    def refresh(self):
        """
        update the screen
        """
        if not self.visible:
            return

        if not self.running:
            return
        
        # Calculate some new values
        if not self.item.length:
            self.item.remain = 0
        else:
            self.item.remain = self.item.length - self.item.elapsed
        self.draw_engine.draw(self.item)


    def eventhandler(self, event):
        """
        React on some events or send them to the real player or the
        item belongig to the player
        """
        if event == PLAY_END and event.arg:
            self.player.stop()
            if self.try_next_player():
                return True
            
        if event in ( STOP, PLAY_END, USER_END ):
            self.stop()
            return self.item.eventhandler(event)

        # try the real player
        if self.player.eventhandler(event):
            return True

        # give it to the item
        return self.item.eventhandler(event)

