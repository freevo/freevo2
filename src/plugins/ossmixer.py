# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# ossmixer.py - The mixer interface for freevo.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# I propose this could replace 'mixer.py' when it's been tested adequately. It
# should also work unchanged under BSD.
#
# Last note, here is the documentation again:
# http://www.python.org/doc/current/lib/mixer-device-objects.html
#
# And to activate:
#
# plugin.remove('mixer')
# plugin.activate('ossmixer')
#
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.7  2004/01/02 14:03:32  dischi
# use osd to display volume
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


"""For manipulating the mixer.
"""

import struct
import os

import config
import plugin
import rc
from event import *

import ossaudiodev


class PluginInterface(plugin.DaemonPlugin):
    SOUND_MIXER_LINE = 7
    SOUND_MASK_LINE = 64
    
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.plugin_name = 'MIXER'
        self.mixfd = None
        self.muted = 0
        
        # If you're using ALSA or something and you don't set the mixer, why are
        # we trying to open it?
        if config.DEV_MIXER:    
            try:
                self.mixfd = ossaudiodev.openmixer() #open(config.DEV_MIXER, 'r')
            except IOError:
                print 'Couldn\'t open mixer %s' % config.DEV_MIXER
                return

        if 0:
            self.mainVolume   = 0
            self.pcmVolume    = 0
            self.lineinVolume = 0
            self.micVolume    = 0
            self.igainVolume  = 0 
            self.ogainVolume  = 0

        if config.MAJOR_AUDIO_CTRL == 'VOL':
            self.setMainVolume(config.DEFAULT_VOLUME)
            if config.CONTROL_ALL_AUDIO:
                self.setPcmVolume(config.MAX_VOLUME)
                self.setOgainVolume(config.MAX_VOLUME)
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            self.setPcmVolume(config.DEFAULT_VOLUME)
            if config.CONTROL_ALL_AUDIO:
                self.setMainVolume(config.MAX_VOLUME)
                self.setOgainVolume(config.MAX_VOLUME)
        else:
            _debug_("No appropriate audio channel found for mixer")

        if config.CONTROL_ALL_AUDIO:
            self.setLineinVolume(0)
            self.setMicVolume(0)


    def eventhandler(self, event = None, menuw=None, arg=None):
        """
        eventhandler to handle the VOL events
        """
        # Handle volume control
        if event == MIXER_VOLUP:
            if config.MAJOR_AUDIO_CTRL == 'VOL':
                self.incMainVolume()
                rc.post_event(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
            elif config.MAJOR_AUDIO_CTRL == 'PCM':
                self.incPcmVolume()
                rc.post_event(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
            return True
        
        elif event == MIXER_VOLDOWN:
            if config.MAJOR_AUDIO_CTRL == 'VOL':
                self.decMainVolume()
                rc.post_event(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
            elif config.MAJOR_AUDIO_CTRL == 'PCM':
                self.decPcmVolume()
                rc.post_event(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
            return True

        elif event == MIXER_MUTE:
            if self.getMuted() == 1:
                rc.post_event(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
                self.setMuted(0)
            else:
                rc.post_event(Event(OSD_MESSAGE, arg=_('Mute')))
                self.setMuted(1)
            return True

        return False



    def _setVolume(self, device, volume):
        if self.mixfd and (self.mixfd.controls() & (1 << device)):
            if volume < 0:
                volume = 0
            if volume > 100:
                volume = 100
            self.mixfd.set(device, (volume,volume))

    def getMuted(self):
        return(self.muted)

    def setMuted(self, mute):
        self.muted = mute
        if mute == 1:
            self._setVolume(ossaudiodev.SOUND_MIXER_VOLUME, 0)
        else:
            self._setVolume(ossaudiodev.SOUND_MIXER_VOLUME, self.mainVolume)

    def getVolume(self):
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            return self.mainVolume
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            return self.pcmVolume
        
    def getMainVolume(self):
        return self.mainVolume

    def setMainVolume(self, volume):
        self.mainVolume = volume
        self._setVolume(ossaudiodev.SOUND_MIXER_VOLUME, self.mainVolume)

    def incMainVolume(self):
        self.mainVolume += 5
        if self.mainVolume > 100:
            self.mainVolume = 100
        self._setVolume(ossaudiodev.SOUND_MIXER_VOLUME, self.mainVolume)

    def decMainVolume(self):
        self.mainVolume -= 5
        if self.mainVolume < 0:
            self.mainVolume = 0
        self._setVolume(ossaudiodev.SOUND_MIXER_VOLUME, self.mainVolume)

    def getPcmVolume(self):
        return self.pcmVolume
    
    def setPcmVolume(self, volume):
        self.pcmVolume = volume
        self._setVolume(ossaudiodev.SOUND_MIXER_PCM, volume)

    def incPcmVolume(self):
        self.pcmVolume += 5
        if self.pcmVolume > 100:
            self.pcmvolume = 100
        self._setVolume( ossaudiodev.SOUND_MIXER_PCM, self.pcmVolume )

    def decPcmVolume(self):
        self.pcmVolume -= 5
        if self.pcmVolume < 0:
            self.pcmVolume = 0
        self._setVolume( ossaudiodev.SOUND_MIXER_PCM, self.pcmVolume )
    
    def setLineinVolume(self, volume):
        if config.CONTROL_ALL_AUDIO:
            self.lineinVolume = volume
            self._setVolume(ossaudiodev.SOUND_MIXER_LINE, volume)

    def getLineinVolume(self):
        return self.lineinVolume
       
    def setMicVolume(self, volume):
        if config.CONTROL_ALL_AUDIO:
            self.micVolume = volume
            self._setVolume(ossaudiodev.SOUND_MIXER_MIC, volume)

    def setIgainVolume(self, volume):
        if config.CONTROL_ALL_AUDIO:
            if volume > 100:
                volume = 100 
            elif volume < 0:
                volume = 0
            self._setVolume(ossaudiodev.SOUND_MIXER_IGAIN, volume)

    def getIgainVolume(self):
        return self.igainVolume

    def decIgainVolume(self):
        self.igainVolume -= 5
        if self.igainVolume < 0:
            self.igainVolume = 0
        self._setVolume(ossaudiodev.SOUND_MIXER_IGAIN, volume)
        
    def incIgainVolume(self):
        self.igainVolume += 5
        if self.igainVolume > 100:
            self.igainVolume = 100
        self._setVolume(ossaudiodev.SOUND_MIXER_IGAIN, volume)

    def setOgainVolume(self, volume):
        if volume > 100:
            volume = 100 
        elif volume < 0:
            volume = 0
        self.ogainVolume = volume
        self._setVolume(ossaudiodev.SOUND_MIXER_IGAIN, volume)

    def reset(self):
        if config.CONTROL_ALL_AUDIO:
            self.setLineinVolume(0)
            self.setMicVolume(0)
            if config.MAJOR_AUDIO_CTRL == 'VOL':
                self.setPcmVolume(config.MAX_VOLUME)
            elif config.MAJOR_AUDIO_CTRL == 'PCM':
                self.setMainVolume(config.MAX_VOLUME)

        self.setIgainVolume(0) # SB Live input from TV Card.
