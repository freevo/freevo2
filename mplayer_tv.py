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
# Revision 1.7  2002/10/06 14:41:22  dischi
# Only use -wid when config.MPLAYER_USE_WID is true
#
# Revision 1.6  2002/08/22 04:45:13  krister
# Changed the test-mplayer to the main one.
#
# Revision 1.5  2002/08/21 04:58:26  krister
# Massive changes! Obsoleted all osd_server stuff. Moved vtrelease and matrox stuff to a new dir fbcon. Updated source to use only the SDL OSD which was moved to osd.py. Changed the default TV viewing app to mplayer_tv.py. Changed configure/setup_build.py/config.py/freevo_config.py to generate and use a plain-text config file called freevo.conf. Updated docs. Changed mplayer to use -vo null when playing music. Fixed a bug in music playing when the top dir was empty.
#
# Revision 1.4  2002/08/20 02:30:25  krister
# Fixed the sound for tv/vcr viewing.
#
# Revision 1.3  2002/08/19 02:06:57  krister
# Added X11 TV viewing. Use the TV norm, chanlist etc from the config file.
#
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

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading
import signal

import util    # Various utilities
import menu    # The menu widget class
import skin    # The skin class
import mixer   # The mixer class
import osd     # The OSD class, used to communicate with the OSD daemon
import rc      # The RemoteControl class.
import music   # The Music module
import movie   # The Movie module
import tv      # The TV module
import imenu   # The Image viewer module
import mplayer
import childapp # Handle child applications

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
        self.xwin_wid = 0
        

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

        
    def Play(self, mode, tuner_channel=None, channel_change=0):

        if tuner_channel != None:
            
            try:
                self.TunerSetChannel(tuner_channel)
            except ValueError:
                pass

        if mode == 'tv':
            tuner_channel = self.TunerGetChannel()

            cf_norm, cf_input, cf_clist = config.TV_SETTINGS.split()

            # Convert to MPlayer TV setting strings
            norm = 'norm=%s' % cf_norm.upper()
            tmp = { 'television':0, 'composite1':1}[cf_input.lower()]
            input = 'input=%s' % tmp
            chanlist = 'chanlist=%s' % cf_clist

            w, h = config.TV_VIEW_SIZE
            outfmt = 'outfmt=%s' % config.TV_VIEW_OUTFMT

            tvcmd = ('-tv on:driver=v4l:%s:%s:channel=%s:'
                     '%s:width=%s:height=%s:%s' %
                     (input, norm, tuner_channel, chanlist, w, h, outfmt))
            
            mpl = ('%s -vo %s -fs %s %s' %
                   (config.MPLAYER_CMD, config.MPLAYER_VO_DEV, tvcmd,
                    config.MPLAYER_ARGS_TVVIEW))

        elif mode == 'vcr':
            cf_norm, cf_input, tmp = config.VCR_SETTINGS.split()

            # Convert to MPlayer TV setting strings
            norm = 'norm=%s' % cf_norm.upper()
            tmp = { 'television':0, 'composite1':1}[cf_input.lower()]
            input = 'input=%s' % tmp

            w, h = config.TV_VIEW_SIZE
            outfmt = 'outfmt=%s' % config.TV_VIEW_OUTFMT
            
            tvcmd = ('-tv on:driver=v4l:%s:%s:channel=2:'
                     'chanlist=us-cable:width=%s:height=%s:%s' %
                     (input, norm, w, h, outfmt))
            
            mpl = ('%s -vo %s -fs %s %s' %
                   (config.MPLAYER_CMD, config.MPLAYER_VO_DEV, tvcmd,
                    config.MPLAYER_ARGS_TVVIEW))

        else:
            print 'Mode "%s" is not implemented' % mode  # XXX ui.message()
            rc.app = None
            menuwidget.refresh()
            return

        # Support for X11, getting the keyboard events
        if self.xwin_wid:  # This is set to 0 when freevo_xwin is killed
            # Already got a freevo_xwin up and running
            wid = self.xwin_wid
            mpl += ' -wid 0x%08x -xy %s -monitoraspect 4:3' % (wid, osd.width)
        elif os.path.isfile('./freevo_xwin') and osd.sdl_driver == 'x11' and \
             config.MPLAYER_USE_WID:
            if DEBUG: print 'Got freevo_xwin and x11'
            os.system('rm -f /tmp/freevo.wid')
            os.system('./freevo_xwin  0 0 %s %s > /tmp/freevo.wid &' %
                      (osd.width, osd.height))

            # Wait until freevo_xwin signals us, but have a timeout so we
            # don't hang here if something goes wrong!
            delay_ms = 50
            timeout_ms = 5000
            while 1:
                if os.path.isfile('/tmp/freevo.wid'):
                    # Check if the whole line has been written yet
                    val = open('/tmp/freevo.wid').read()
                    if len(val) > 5 and val[-1] == '\n':
                        break
                time.sleep(delay_ms / 1000.0)
                timeout_ms -= delay_ms
                if timeout_ms < 0.0:
                    print 'Could not start freevo_xwin!'  # XXX ui.message()
                    return

            if DEBUG: print 'Got freevo.wid'
            try:
                wid = int(open('/tmp/freevo.wid').read().strip(), 16)
                self.xwin_wid = wid
                mpl += ' -wid 0x%08x -xy %s -monitoraspect 4:3' % (wid, osd.width)
                if DEBUG: print 'Got WID = 0x%08x' % wid
            except:
                print 'Cannot access freevo_xwin data!'   # XXX ui.message()
                pass

        command = mpl
                
        self.mode = mode

        # XXX Mixer manipulation code.
        # TV is on line in
        # VCR is mic in
        # btaudio (different dsp device) will be added later
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer_vol = mixer.getMainVolume()
            mixer.setMainVolume(0)
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer_vol = mixer.getPcmVolume()
            mixer.setPcmVolume(0)

        # clear the screen for mplayer
        osd.clearscreen(color=osd.COL_BLACK)
        osd.update()
        
        # Start up the TV task
        self.thread.mode = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        
        rc.app = self.EventHandler

        # Suppress annoying audio clicks
        time.sleep(0.4)
        # XXX Hm.. This is hardcoded and very unflexible.
        if mode == 'vcr':
            mixer.setMicVolume(config.VCR_IN_VOLUME)
        else:
            mixer.setLineinVolume(config.TV_IN_VOLUME)
            mixer.setIgainVolume(config.TV_IN_VOLUME)
            
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setMainVolume(mixer_vol)
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setPcmVolume(mixer_vol)

        if DEBUG: print '%s: started %s app' % (time.time(), self.mode)

        skin.hold = TRUE  # Prevent the skin from drawing stuff while TV is on
        
        
    def Stop(self, channel_change=0):
        # XXX Kludge for now. do real channelchange in mplayer later
        if not channel_change:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            mixer.setIgainVolume(0) # Input on emu10k cards.

        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.05)
        print 'stopped %s app' % self.mode
        os.system('rm -f /tmp/freevo.wid')


    def EventHandler(self, event):
        print '%s: %s app got %s event' % (time.time(), self.mode, event)
        if (event == rc.MENU or event == rc.STOP or event == rc.EXIT or
            event == rc.SELECT or event == rc.PLAY_END):
            self.Stop()
            os.system('killall -9 freevo_xwin 2&> /dev/null')
            self.xwin_wid = 0
            skin.hold = FALSE  # Allow drawing again
            rc.app = None
            menuwidget.refresh()

        elif event == rc.CHUP:
            if self.mode == 'vcr':
                return
            
            # Go to the next channel in the list
            self.TunerNextChannel()
            self.Stop(channel_change=1)
            self.Play(mode='tv')  # Mplayer can only set the channel when starting up
            
        elif event == rc.CHDOWN:
            if self.mode == 'vcr':
                return
            
            # Go to the previous channel in the list
            self.TunerPrevChannel()
            self.Stop(channel_change=1)
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
        # XXX Krister testcode for proper X11 video
        if DEBUG: print 'Killing mplayer'

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
