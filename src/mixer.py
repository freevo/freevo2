#if 0 /*
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
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
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
"""For manipulating the mixer.
"""

import fcntl
import struct
import config
import os     # system() is used to manipulate the mixer for SB Live cards.

# Set to 1 for debug output
DEBUG = config.DEBUG

# Module variable that contains an initialized Mixer() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Mixer()
        
    return _singleton


class Mixer:
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
        try:
            self.mixfd        = open(config.DEV_MIXER, 'r')
        except IOError:
            print 'Couldnt open mixer %s!' % config.DEV_MIXER
            self.mixfd = None
            return
        
        self.mainVolume   = 0
        self.pcmVolume    = 0
        self.lineinVolume = 0
        self.micVolume    = 0
        self.igainVolume  = 0 # XXX Used on SB Live
        self.ogainVolume  = 0 # XXX Ditto
        
        # Gustavo: By default, don't change the values to zero
        # self.setMainVolume(self.mainVolume)
        # self.setPcmVolume(self.pcmVolume)
        # self.setLineinVolume(self.lineinVolume)
        #  self.setMicVolume(self.micVolume)

        if self.mixfd:
            data = struct.pack( 'L', self.SOUND_MASK_LINE )
            fcntl.ioctl( self.mixfd.fileno(), self.SOUND_MIXER_WRITE_RECSRC, data )
        
    def _setVolume(self, device, volume):
        if self.mixfd:
            if DEBUG: print 'Volume = %d' % volume
            if volume < 0: volume = 0
            if volume > 100: volume = 100
            vol = (volume << 8) | (volume)
            data = struct.pack('L', vol)
            fcntl.ioctl(self.mixfd.fileno(), device, data)

    def getMainVolume(self):
        return(self.mainVolume)
        
    def setMainVolume(self, volume):
        self.mainVolume = volume
        self._setVolume(self.SOUND_MIXER_WRITE_VOLUME, self.mainVolume)
        
    def incMainVolume(self):
        self.mainVolume += 5
        if self.mainVolume > 100: self.mainVolume = 100
        self._setVolume(self.SOUND_MIXER_WRITE_VOLUME, self.mainVolume)

    def decMainVolume(self):
        self.mainVolume -= 5
        if self.mainVolume < 0: self.mainVolume = 0
        self._setVolume(self.SOUND_MIXER_WRITE_VOLUME, self.mainVolume)

    def getPcmVolume(self):
        return( self.pcmVolume )
    
    def setPcmVolume(self, volume):
        self.pcmVolume = volume
        self._setVolume(self.SOUND_MIXER_WRITE_PCM, volume)

    def incPcmVolume(self):
        self.pcmVolume += 5
        if self.pcmVolume > 100: self.pcmvolume = 100
        self._setVolume( self.SOUND_MIXER_WRITE_PCM, self.pcmVolume )

    def decPcmVolume(self):
        self.pcmVolume -= 5
        if self.pcmVolume < 0: self.pcmVolume = 0
        self._setVolume( self.SOUND_MIXER_WRITE_PCM, self.pcmVolume )
    
    def setLineinVolume(self, volume):
        self.lineinVolume = volume
        self._setVolume(self.SOUND_MIXER_WRITE_LINE, volume)

    def getLineinVolume(self):
        return self.lineinVolume
       
    def setMicVolume(self, volume):
        self.micVolume = volume
        self._setVolume(self.SOUND_MIXER_WRITE_MIC, volume)

    def setIgainVolume(self, volume):
        """For Igain (input from TV etc) on emu10k cards"""
        if volume > 100: volume = 100 
        elif volume < 0: volume = 0
        self.igainVolume = volume
        os.system('aumix -i%s &> /dev/null &' % volume)

    def getIgainVolume(self):
        return self.igainVolume

    def decIgainVolume(self):
        self.igainVolume -= 5
        if self.igainVolume < 0: self.igainVolume = 0
        os.system('aumix -i-5 &> /dev/null &')
        
    def incIgainVolume(self):
        self.igainVolume += 5
        if self.igainVolume > 100: self.igainVolume = 100
        os.system('aumix -i+5 &> /dev/null &')
        
    def setOgainVolume(self, volume):
        """For Ogain on SB Live Cards"""
        if volume > 100: volume = 100 
        elif volume < 0: volume = 0
        self.ogainVolume = volume
        os.system('aumix -o%s &> /dev/null &' % volume)


# Simple test...
if __name__ == '__main__':
    mixer = Mixer()
    mixer.setPcmVolume(50)
    
