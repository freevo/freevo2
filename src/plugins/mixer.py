# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mixer.py - The mixer interface for freevo.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.18  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.17  2004/11/01 20:15:40  dischi
# fix debug
#
# Revision 1.16  2004/10/21 12:32:22  dischi
# fix variable type
#
# Revision 1.15  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.14  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.13  2004/01/02 14:03:32  dischi
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

import fcntl
import struct
import os

import config
import eventhandler
import plugin
from event import *

import logging
log = logging.getLogger()

class PluginInterface(plugin.DaemonPlugin):
    # These magic numbers were determined by writing a C-program using the
    # macros in /usr/include/linux/... and printing the values.
    # They seem to work on my machine. XXX Is there a real python interface?
    SOUND_MIXER_WRITE_VOLUME = 0xc0044d00
    SOUND_MIXER_WRITE_PCM = 0xc0044d04
    SOUND_MIXER_WRITE_LINE = 0xc0044d06
    SOUND_MIXER_WRITE_MIC = 0xc0044d07
    SOUND_MIXER_WRITE_RECSRC = 0xc0044dff
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
                self.mixfd = open(config.DEV_MIXER, 'r')
            except IOError:
                log.error('Couldn\'t open mixer %s' % config.DEV_MIXER)
                return

        if 0:
            self.mainVolume   = 0
            self.pcmVolume    = 0
            self.lineinVolume = 0
            self.micVolume    = 0
            self.igainVolume  = 0 # XXX Used on SB Live
            self.ogainVolume  = 0 # XXX Ditto

            if self.mixfd:
                data = struct.pack( 'L', self.SOUND_MASK_LINE )
                try:
                    fcntl.ioctl( self.mixfd.fileno(), self.SOUND_MIXER_WRITE_RECSRC, data )
                except IOError:
                    log.error('IOError for ioctl')
                    pass
                
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            self.setMainVolume(config.DEFAULT_VOLUME)
            if config.CONTROL_ALL_AUDIO:
                self.setPcmVolume(config.MAX_VOLUME)
                # XXX This is for SB Live cards should do nothing to others
                # XXX Please tell if you have problems with this.
                self.setOgainVolume(config.MAX_VOLUME)
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            self.setPcmVolume(config.DEFAULT_VOLUME)
            if config.CONTROL_ALL_AUDIO:
                self.setMainVolume(config.MAX_VOLUME)
                # XXX This is for SB Live cards should do nothing to others
                # XXX Please tell if you have problems with this.
                self.setOgainVolume(config.MAX_VOLUME)
        else:
            log.warning("No appropriate audio channel found for mixer")

        if config.CONTROL_ALL_AUDIO:
            self.setLineinVolume(0)
            self.setMicVolume(0)


    def eventhandler(self, event = None, menuw=None, arg=None):
        """
        eventhandler to handle the VOL events
        """
        if event == MIXER_VOLUP:
            if config.MAJOR_AUDIO_CTRL == 'VOL':
                self.incMainVolume(event.arg)
                eventhandler.post(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
            elif config.MAJOR_AUDIO_CTRL == 'PCM':
                self.incPcmVolume(event.arg)
                eventhandler.post(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
            return True
        
        elif event == MIXER_VOLDOWN:
            if( config.MAJOR_AUDIO_CTRL == 'VOL' ):
                self.decMainVolume(event.arg)
                eventhandler.post(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
            elif( config.MAJOR_AUDIO_CTRL == 'PCM' ):
                self.decPcmVolume(event.arg)
                eventhandler.post(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
            return True

        elif event == MIXER_MUTE:
            if self.getMuted() == 1:
                eventhandler.post(Event(OSD_MESSAGE, arg=_('Volume: %s%%') % self.getVolume()))
                self.setMuted(0)
            else:
                eventhandler.post(Event(OSD_MESSAGE, arg=_('Mute')))
                self.setMuted(1)
            return True

        return False



    def _setVolume(self, device, volume):
        if self.mixfd:
            if volume < 0:
                volume = 0
            if volume > 100:
                volume = 100
            vol = (volume << 8) | (volume)
            data = struct.pack('L', vol)
            try:
                fcntl.ioctl(self.mixfd.fileno(), device, data)
            except IOError:
                log.error('IOError for ioctl')
                pass
            
    def getMuted(self):
        return(self.muted)

    def setMuted(self, mute):
        self.muted = mute
        if mute == 1:
            self._setVolume(self.SOUND_MIXER_WRITE_VOLUME, 0)
        else:
            self._setVolume(self.SOUND_MIXER_WRITE_VOLUME, self.mainVolume)

    def getVolume(self):
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            return self.mainVolume
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            return self.pcmVolume
        
    def getMainVolume(self):
        return(self.mainVolume)

    def setMainVolume(self, volume):
        self.mainVolume = volume
        self._setVolume(self.SOUND_MIXER_WRITE_VOLUME, self.mainVolume)

    def incMainVolume(self, step=5):
        self.mainVolume += step
        if self.mainVolume > 100:
            self.mainVolume = 100
        self._setVolume(self.SOUND_MIXER_WRITE_VOLUME, self.mainVolume)

    def decMainVolume(self, step=5):
        self.mainVolume -= step
        if self.mainVolume < 0:
            self.mainVolume = 0
        self._setVolume(self.SOUND_MIXER_WRITE_VOLUME, self.mainVolume)

    def getPcmVolume(self):
        return self.pcmVolume
    
    def setPcmVolume(self, volume):
        self.pcmVolume = volume
        self._setVolume(self.SOUND_MIXER_WRITE_PCM, volume)

    def incPcmVolume(self, step=5):
        self.pcmVolume += step
        if self.pcmVolume > 100:
            self.pcmVolume = 100
        self._setVolume( self.SOUND_MIXER_WRITE_PCM, self.pcmVolume )

    def decPcmVolume(self, step=5):
        self.pcmVolume -= step
        if self.pcmVolume < 0:
            self.pcmVolume = 0
        self._setVolume( self.SOUND_MIXER_WRITE_PCM, self.pcmVolume )
    
    def setLineinVolume(self, volume):
        if config.CONTROL_ALL_AUDIO:
            self.lineinVolume = volume
            self._setVolume(self.SOUND_MIXER_WRITE_LINE, volume)

    def getLineinVolume(self):
        return self.lineinVolume
       
    def setMicVolume(self, volume):
        if config.CONTROL_ALL_AUDIO:
            self.micVolume = volume
            self._setVolume(self.SOUND_MIXER_WRITE_MIC, volume)

    def setIgainVolume(self, volume):
        """For Igain (input from TV etc) on emu10k cards"""
        if config.CONTROL_ALL_AUDIO:
            if volume > 100:
                volume = 100 
            elif volume < 0:
                volume = 0
            self.igainVolume = volume
            os.system('aumix -i%s > /dev/null 2>&1 &' % volume)

    def getIgainVolume(self):
        return self.igainVolume

    def decIgainVolume(self, step=5):
        self.igainVolume -= step
        if self.igainVolume < 0:
            self.igainVolume = 0
        os.system('aumix -i-%s > /dev/null 2>&1 &' % step)
        
    def incIgainVolume(self, step=5):
        self.igainVolume += step
        if self.igainVolume > 100:
            self.igainVolume = 100
        os.system('aumix -i+%s > /dev/null 2>&1 &' % step)
        
    def setOgainVolume(self, volume):
        """For Ogain on SB Live Cards"""
        if volume > 100:
            volume = 100 
        elif volume < 0:
            volume = 0
        self.ogainVolume = volume
        os.system('aumix -o%s > /dev/null 2>&1' % volume)

    def reset(self):
        if config.CONTROL_ALL_AUDIO:
            self.setLineinVolume(0)
            self.setMicVolume(0)
            if config.MAJOR_AUDIO_CTRL == 'VOL':
                self.setPcmVolume(config.MAX_VOLUME)
            elif config.MAJOR_AUDIO_CTRL == 'PCM':
                self.setMainVolume(config.MAX_VOLUME)

        self.setIgainVolume(0) # SB Live input from TV Card.
