#if 0 /*
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer module for audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/01/11 10:55:56  dischi
# Call refresh with reload=1 when the menu was disabled during playback
#
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

import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading, signal

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import menu       # The menu widget class
import mixer      # Controls the volumes for playback and recording
import osd        # The OSD class, used to communicate with the OSD daemon
import rc         # The RemoteControl class.
import skin       # Cause audio handling needs skin functions.
import fnmatch

# RegExp
import re

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# Setting up the default objects:
osd        = osd.get_singleton()
rc         = rc.get_singleton()
menuwidget = menu.get_singleton()
mixer      = mixer.get_singleton()
skin       = skin.get_singleton()

# Module variable that contains an initialized MPlayer() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MPlayer()
        
    return _singleton

def get_demuxer(filename):
    DEMUXER_MP3 = 17
    DEMUXER_OGG = 18
    rest, extension     = os.path.splitext(filename)
    if string.lower(extension) == '.mp3':
        return "-demuxer " + str(DEMUXER_MP3)
    if string.lower(extension) == '.ogg':
        return "-demuxer " + str(DEMUXER_OGG)
    else:
        return ''


class MPlayer:
    """
    the main class to control mplayer
    """
    
    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.start()
        self.mode = None

                         
    def play(self, item):
        """
        play a audioitem with mplayer
        """
        filename = item.filename

        # Is the file streamed over the network?
        if filename.find('://') != -1:
            # Yes, trust the given mode
            network_play = 1
        else:
            network_play = 0

        if not os.path.isfile(filename) and not network_play:
	    skin.PopupBox('%s\nnot found!' % os.path.basename(filename))
            time.sleep(2.0) 
            menuwidget.refresh()
            # XXX We should really use return more. And this escape should
            # XXX probably be put at start of the function.
            return 0
       
        # Build the MPlayer command
        mpl = '--prio=%s %s %s' % (config.MPLAYER_NICE,
                                   config.MPLAYER_CMD,
                                   config.MPLAYER_ARGS_DEF)

        if not network_play:
            demux = ' %s ' % get_demuxer(filename)
        else:
            # Don't include demuxer for network files
            demux = ''

        command = '%s -vo null %s "%s"' % (mpl, demux, filename)
                
        self.item = item

        # XXX A better place for the major part of this code would be
        # XXX mixer.py
        if config.CONTROL_ALL_AUDIO:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            if config.MAJOR_AUDIO_CTRL == 'VOL':
                mixer.setPcmVolume(config.MAX_VOLUME)
            elif config.MAJOR_AUDIO_CTRL == 'PCM':
                mixer.setMainVolume(config.MAX_VOLUME)
                
        mixer.setIgainVolume(0) # SB Live input from TV Card.
        # This should _really_ be set to zero when playing other audio.

        self.thread.item = item

        if self.thread.item.valid:
            item.drawall = 1
            skin.DrawMP3(self.item) 
            self.item.drawall = 0
        else:
            # Invalid file, show an error and survive.
            skin.PopupBox('Invalid audio file')
            time.sleep(3.0)
            menuwidget.refresh()
            return

        self.thread.play_mode = self.mode

        if DEBUG:
            print 'MPlayer.play(): Starting thread, cmd=%s' % command
            
        self.thread.mode    = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        rc.app = self.eventhandler


    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        rc.app = None
        self.thread.item = None
        while self.thread.mode == 'stop':
            time.sleep(0.3)


    def eventhandler(self, event):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if event == rc.EXIT or event == rc.STOP:
            self.thread.item = None
            self.stop ()
            rc.app = None
            menuwidget.refresh(reload=1)

        elif event == rc.PAUSE:
            self.thread.cmd('pause')

        elif event == rc.FFWD:
            self.thread.cmd('skip_forward')

        elif event == rc.RIGHT:
            self.thread.cmd('skip_forward2')

        elif event == rc.REW:
            self.thread.cmd('skip_back')

        elif event == rc.LEFT:
            self.thread.cmd('skip_back2')

        elif event == rc.PLAY_END:
            self.stop()
            rc.app = None
            # PLAY_END may also be important for the item
            return self.item.eventhandler(event)
        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)
            
            
# ======================================================================

class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, app, item):
        self.item = item
        self.elapsed = 0
        childapp.ChildApp.__init__(self, app)
        self.RE_TIME = re.compile("^A: +([0-9]+)\.").match


    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)


    def stdout_cb(self, str):
        if config.MPLAYER_DEBUG:
            fd = open('./mplayer_stdout.log', 'a')
            fd.write(str + '\n')
            fd.close()
                     
        if str.find("A:") == 0:         # get current time
            m = self.RE_TIME(str)
            if m:
                self.item.elapsed = int(m.group(1))
                if self.item.elapsed != self.elapsed:
                    self.item.draw()
                self.elapsed = self.item.elapsed


    def stderr_cb(self, str):
        if config.MPLAYER_DEBUG:
            fd = open('./mplayer_stderr.log', 'a')
            fd.write(str + '\n')
            fd.close()
                     

# ======================================================================

class MPlayer_Thread(threading.Thread):
    """
    Thread to wait for a mplayer command to play
    """
    
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.play_mode = ''
        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None
        self.item      = None

        
    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'play':

                if DEBUG:
                    print 'MPlayer_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = MPlayerApp(self.command, self.item)

                while self.mode == 'play' and self.app.isAlive():
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
        'QUIT'           : 'q',
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
