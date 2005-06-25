# -*- coding: iso-8859-1 -*-
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
# Revision 1.14  2005/06/25 08:52:24  dischi
# switch to new style python classes
#
# Revision 1.13  2005/06/24 20:51:39  dischi
# remove USER_END and self.parent.current_item
#
# Revision 1.12  2005/06/09 19:43:53  dischi
# clean up eventhandler usage
#
# Revision 1.11  2004/08/01 10:41:52  dischi
# deactivate plugin
#
# Revision 1.10  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.9  2004/01/20 00:24:20  mikeruelle
# update elapsed time for radio in a thread
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


import time, os
import string
import re
import thread

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
        self.reason = config.REDESIGN_UNKNOWN
        return
        plugin.Plugin.__init__(self)

        # register it as the object to play audio
        plugin.register(RadioPlayer(), plugin.AUDIO_PLAYER, True)

class RadioPlayer(object):

    def __init__(self):
        self.mode = 'idle'
        self.name = 'radioplayer'
        self.app_mode = 'audio'
        self.app = None
	self.starttime = 0

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
	self.item.elapsed = 0
	self.starttime = time.time()

        print 'RadioPlayer.play() %s' % self.item.station
            
        self.mode    = 'play'
        mixer = plugin.getbyname('MIXER')
        mixer.setLineinVolume(config.TV_IN_VOLUME)
        mixer.setIgainVolume(config.TV_IN_VOLUME)
        mixer.setMicVolume(config.TV_IN_VOLUME)
        os.system('%s -qf %s' % (config.RADIO_CMD, self.item.station))
	thread.start_new_thread(self.__update_thread, ())
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
	self.item.elapsed = int(time.time() - self.starttime)
        self.playerGUI.refresh()
        

    def eventhandler(self, event):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        print 'Radio Player event handler %s' % event
        if event in ( STOP, PLAY_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)

    def __update_thread(self):
        """
        OSD update thread
        """
        while self.is_playing():
            self.refresh()
            time.sleep(0.3)

