#
# mixer.py
#
# This is the mixer interface
#
# $Id$

import fcntl, struct

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Set to 1 for debug output
DEBUG = 0

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
        self.mixfd = open('/dev/mixer', 'r')   # XXX Hardcoded to mixer0
        self.mainVolume = 0
        self.pcmVolume = 0
        self.lineinVolume = 0
        self.micVolume = 0
        self.setMainVolume(self.mainVolume)
        self.setPcmVolume(self.pcmVolume)
        self.setLineinVolume(self.lineinVolume)
        self.setMicVolume(self.micVolume)
        data = struct.pack('L', self.SOUND_MASK_LINE)
        fcntl.ioctl(self.mixfd.fileno(), self.SOUND_MIXER_WRITE_RECSRC, data)
        
        
    def _setVolume(self, device, volume):
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

        
    def setPcmVolume(self, volume):
        self._setVolume(self.SOUND_MIXER_WRITE_PCM, volume)

        
    def setLineinVolume(self, volume):
        self._setVolume(self.SOUND_MIXER_WRITE_LINE, volume)
       

    def setMicVolume(self, volume):
        self._setVolume(self.SOUND_MIXER_WRITE_MIC, volume)
       

# Simple test...
if __name__ == '__main__':
    mixer = Mixer()
    mixer.setPcmVolume(50)
    
