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
# Revision 1.8  2004/01/14 20:54:02  mikeruelle
# umm that's a little bit better
#
# Revision 1.7  2004/01/14 20:38:07  mikeruelle
# it's still broken. help dischi.
#
# Revision 1.6  2004/01/10 21:27:37  mikeruelle
# forgot the little  q in the arg. really need to get a card with radio to test
#
# Revision 1.5  2003/12/10 19:10:35  dischi
# AUDIO_PLAY_END is not needed anymore
#
# Revision 1.4  2003/09/22 20:36:18  mikeruelle
# more web interface help descriptions
#
# Revision 1.3  2003/09/20 09:42:32  dischi
# cleanup
#
# Revision 1.2  2003/09/01 19:46:02  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.1  2003/08/27 15:30:12  mikeruelle
# Start of Radio Support
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
import plugin

from event import *


class PluginInterface(plugin.Plugin):
    """
    This is the player plugin for the radio. Basically it tunes all the
    radio stations set in the radio plugin and does the interaction
    between the radio command line program and freevo. please see the
    audio.radio plugin for setup information  

    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        # register it as the object to play audio
        plugin.register(RadioPlayer(), plugin.AUDIO_PLAYER, True)

class RadioPlayer:

    def __init__(self):
        self.mode = 'idle'
        self.name = 'radioplayer'
        self.app_mode = 'audio'
        self.app = None

    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.url.startswith('radio://'):
            return 2
        return 0


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
        os.system('%s -qm' % config.RADIO_CMD)


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
        if event in ( STOP, PLAY_END, USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)
