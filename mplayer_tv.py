#if 0 /*
# -----------------------------------------------------------------------
# mplayer_tv.py - Temporary implementation of a TV function using
#                 MPlayer. This will be merged into mplayer.py later.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2002/08/17 18:33:36  krister
# Changed format from yv12 to yuy2 (12->16 bpp). Added cache. Still a little jerky sometimes, mplayer will hopefully be fixed soon.
#
# Revision 1.1  2002/08/17 06:15:14  krister
# Mplayer TV module. Requires a patched mplayer, will be in their CVS before september (?). Set MPLAYER_TV = 1 in freevo_config.py to use. Is hardcoded for NTSC, etc right now. This file will merge into mplayer.py later.
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

import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading
import signal


# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# Handle child applications
import childapp

# The menu widget class
import menu

# The mixer class, controls the volumes for playback and recording
import mixer

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# Create the remote control object
rc = rc.get_singleton()


# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

# Create the MenuWidget object
menuwidget = menu.get_singleton()

# Set up the mixer
mixer = mixer.get_singleton()


# Module variable that contains an initialized V4L1TV() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MPlayer()
        
    return _singleton


class MPlayer:

    __muted    = 0
    __igainvol = 0
    
    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.start()
        self.tuner_chidx = 0    # Current channel, index into config.TV_CHANNELS
        

    def TunerSetChannel(self, tuner_channel):
        for pos in range(len(config.TV_CHANNELS)):
            channel = config.TV_CHANNELS[pos]
            if channel[2] == tuner_channel:
                self.tuner_chidx = pos
                return
        print 'ERROR: Cannot find tuner channel "%s" in the TV channel listing' % tuner_channel
        self.tuner_chidx = 0


    def TunerGetChannel(self):
        return config.TV_CHANNELS[self.tuner_chidx][2]


    def TunerNextChannel(self):
        self.tuner_chidx = (self.tuner_chidx+1) % len(config.TV_CHANNELS)


    def TunerPrevChannel(self):
        self.tuner_chidx = (self.tuner_chidx-1) % len(config.TV_CHANNELS)

        
    def Play(self, mode, tuner_channel=None):

        if tuner_channel != None:
            
            try:
                self.TunerSetChannel(tuner_channel)
            except ValueError:
                pass

        if mode == 'tv':
            tuner_channel = self.TunerGetChannel()
            tvcmd = ('-tv on:driver=v4l:input=0:norm=NTSC:channel=%s:'
                     'chanlist=us-cable:width=640:height=480:outfmt=yuy2' % tuner_channel)
            command = ('../apps/mplayer -vo %s -fs %s -cache 3000' %
                       (config.MPLAYER_VO_DEV, tvcmd))
        elif mode == 'vcr':
            raise 'Not implemented'
            command = config.WATCH_TV_APP + ' "' + config.VCR_SETTINGS + ' 2"'  # Channel isn't used
        else:
            raise 'Not implemented'
            now = time.localtime(time.time())
            outfile = time.strftime("0_rec_%Y-%m-%d_%H%M%S.avi", now)
            outfile = config.DIR_RECORD + '/' + outfile
            command = (config.VIDREC_MQ % outfile)

        self.mode = mode

        # XXX Mixer manipulation code.
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setPcmVolume(0)
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setMainVolume(0)
        if config.CONTROL_ALL_AUDIO:
            mixer.setLineinVolume(0)
            mixer.setIgainVolume(0)
            mixer.setMicVolume(0)

        # XXX Should be moved out in appropriate functions.
        osd.clearscreen(color=osd.COL_BLACK)
        osd.drawstring('Running the "%s" application' % mode, 30, 280,
                       fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
        self.thread.mode = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        
        rc.app = self.EventHandler

        # Suppress annoying audio clicks
        time.sleep(0.5)
        # XXX Hm.. This is hardcoded and very unflexible.
        if mode == 'vcr':
            mixer.setMicVolume( config.VCR_IN_VOLUME )
        else:
            mixer.setLineinVolume( config.TV_IN_VOLUME )
            mixer.setIgainVolume( config.TV_IN_VOLUME )
            
        print '%s: started %s app' % (time.time(), self.mode)

        
    def Stop(self):
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setPcmVolume(config.MAX_VOLUME)
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setMainVolume(config.MAX_VOLUME)
        mixer.setLineinVolume(0)
        mixer.setMicVolume(0)
        mixer.setIgainVolume(0) # Input on emu10k cards.

        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.05)
        print 'stopped %s app' % self.mode


    def channel_change(self):
        """This is a helper function for channel up and down events"""
        linein_vol = mixer.getLineinVolume()
        igain_vol  = mixer.getIgainVolume()
        
        mixer.setLineinVolume(0)
        mixer.setIgainVolume(0) # Input from TV om emu10k1 cards.

        tuner_channel = self.TunerGetChannel()
        self.thread.app.write( config.TV_SETTINGS + ' ' +
                               tuner_channel + '\n' )
        time.sleep(0.1)
        mixer.setLineinVolume(linein_vol)
        mixer.setIgainVolume(igain_vol)
        

    def EventHandler(self, event):
        print '%s: %s app got %s event' % (time.time(), self.mode, event)
        if event == rc.MENU or event == rc.STOP or event == rc.SELECT or event == rc.PLAY_END:
            self.Stop()
            rc.app = None
            menuwidget.refresh()

        elif event == rc.CHUP:
            if self.mode == 'vcr':
                return
            # Go to the next channel in the list
            self.TunerNextChannel()
            self.Stop()
            self.Play(mode='tv')  # Mplayer can only set the channel when starting up
            
        elif event == rc.CHDOWN:
            if self.mode == 'vcr':
                return
            # Go to the previous channel in the list
            self.TunerPrevChannel()
            self.Stop()
            self.Play(mode='tv')
            
        elif event == rc.VOLUP:
            mixer.incIgainVolume()

        elif event == rc.VOLDOWN:
            mixer.decIgainVolume()

        elif event == rc.MUTE:
            if self.__muted:
                mixer.setIgainVolume(self.__igainvol)
                self.__muted = 0
            else:
                self.__igainvol = mixer.getIgainVolume()
                mixer.setIgainVolume(0)
                self.__muted = 1
            

# ======================================================================
class MPlayerApp(childapp.ChildApp):
        
    def kill(self):
        childapp.ChildApp.kill(self, signal.SIGINT)
	osd.update()
        # XXX Krister testcode for proper X11 video
        if DEBUG: print 'Killing mplayer'
        os.system('killall -9 freevo_xwin 2&> /dev/null')
        os.system('rm -f /tmp/freevo.wid')

    # def stdout_cb


# ======================================================================
class MPlayer_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None
        self.audioinfo = None              # Added to enable update of GUI

    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
                
            elif self.mode == 'play':

                if DEBUG:
                    print 'MPlayer_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = MPlayerApp(self.command)
                
                while self.mode == 'play' and self.app.isAlive():
                    # if DEBUG: print "Still running..."
                    if self.audioinfo: 
                        if not self.audioinfo.pause:
                            self.audioinfo.draw()        
                    time.sleep(0.1)

                self.app.kill()

                if self.mode == 'play':
                    rc.post_event(rc.PLAY_END)

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'


    def cmd(self, command):
        print "In cmd going to do: " + command
        str = ''
        if command == 'info':
            str = mplayerKey('INFO')
        elif command == 'next':
            str = mplayerKey('NEXT')
        elif command == 'pause':
            str = mplayerKey('PAUSE')
        elif command == 'prev':
            str = mplayerKey('PREV')
        elif command == 'stop':
            str = mplayerKey('STOP')
        elif command == 'skip_forward':
            str = mplayerKey('RIGHT')
        elif command == 'skip_forward2':
            str = mplayerKey('UP')
        elif command == 'skip_forward3':
            str = mplayerKey('PAGEUP')
        elif command == 'skip_back':
            str = mplayerKey('LEFT')
        elif command == 'skip_back2':
            str = mplayerKey('DOWN')
        elif command == 'skip_back3':
            str = mplayerKey('PAGEDOWN')

        print "In cmd going to write: " + str
        self.app.write(str) 


#
# Translate an abstract remote control command to an mplayer
# command key
#
def mplayerKey(rcCommand):
    mplayerKeys = {
        'DOWN'           : '\x1bOB',
        'INFO'           : 'o',
        'KEY_1'          : '+',
        'KEY_7'          : '-',
        'LEFT'           : '\x1bOD',
        'NONE'           : '',
        'NEXT'           : '>',
        'OK'             : 'q',
        'PAGEUP'         : '\x1b[5~',
        'PAGEDOWN'       : '\x1b[6~',
        'PAUSE'          : ' ',
        'PLAY'           : ' ',
        'PREV'           : '<',
        'RIGHT'          : '\x1bOC',
        'STOP'           : 'q',
        'UP'             : '\x1bOA',
        'VOLUMEUP'       : '*',
        'VOLUMEDOWN'     : '/',
        'DISPLAY'        : 'o'
        }
    
    key = mplayerKeys.get(rcCommand, '')

    return key


# Test code
if __name__ == '__main__':
    player = get_singleton()

    player.play('audio', sys.argv[1], None)
