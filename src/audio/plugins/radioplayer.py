#if 0 /*
# -----------------------------------------------------------------------
# radioplayer.py - the Freevo Radioplayer plugin for radio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/09/01 19:46:02  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.1  2003/08/27 15:30:12  mikeruelle
# Start of Radio Support
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
# ----------------------------------------------------------------------- */
#endif

import time, os
import string
import re

import config     # Configuration handler. reads config file.
import util       # Various utilities

import rc
import plugin
from event import *


DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0


class PluginInterface(plugin.Plugin):
    """
    player plugin for the radio player. Use radio player to play all radio
    stations.
    """
    def __init__(self):
        # create the mplayer object
        plugin.Plugin.__init__(self)

        # register it as the object to play audio
        plugin.register(self, plugin.RADIO_PLAYER)
        self.mode = 'idle'

    def play(self, item, playerGUI):
        """
        play a radioitem with radio player
        """
        self.playerGUI = playerGUI
        self.item = item

        print 'RadioPlayer.play() %s' % self.item.station
            
        self.mode    = 'play'
        mixer = plugin.getbyname('MIXER')
        mixer.setLineinVolume(config.TV_IN_VOLUME)
        mixer.setIgainVolume(config.TV_IN_VOLUME)
        mixer.setMicVolume(config.TV_IN_VOLUME)
        os.system('%s -qf %s' % (config.RADIO_CMD, self.item.station))
        return None
    

    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        print 'Radio Player Stop'
        self.mode = 'stop'
        mixer = plugin.getbyname('MIXER')
        mixer.setLineinVolume(0)
        mixer.setIgainVolume(0)
        mixer.setMicVolume(0)
        os.system('%s -m' % config.RADIO_CMD)

    def is_playing(self):
        print 'Radio Player IS PLAYING?'
        return self.mode == 'play'

    def refresh(self):
        print 'Radio Player refresh'
        self.playerGUI.refresh()
        
    def eventhandler(self, event, menuw=None):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        print 'Radio Player event handler %s' % event

        if event == AUDIO_PLAY_END or event == MENU_BACK_ONE_MENU:
            event = PLAY_END

        if event in ( STOP, PLAY_END, USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)
