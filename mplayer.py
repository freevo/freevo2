# ----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer module. 
# ----------------------------------------------------------------------
# $Id$
#
# Authors:     Krister Lagerstrom <krister@kmlager.com>
#              Aubin Paul <aubin@punknews.org>
#              Dirk Meyer <dischi@... >
#              Thomas Malt <thomas@malt.no>
# Notes:
# Todo:        * Add support for Ogg-Vorbis
#              * Start using mplayer as audio player.
#
# ----------------------------------------------------------------------
# $Log$
# Revision 1.14  2002/07/29 05:24:35  outlyer
# Lots and lots of changes for new mplayer-based audio playing code.
# o You'll need to modify your config file, as well as setup the new mplayer
#   module by editing main.py
# o This change includes Ogg Support, but that requires the ogg.vorbis
#   module. If you don't want it, just don't install ogg.vorbis :)
#
# ----------------------------------------------------------------------
# 
# Copyright (C) 2002 Krister Lagerstrom
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
# ----------------------------------------------------------------------
#

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
import audioinfo  # This just for ID3 functions and stuff.
import skin       # Cause audio handling needs skin functions.

DEBUG = 1
TRUE  = 1
FALSE = 0

# Setting up the default objects:
osd        = osd.get_singleton()
rc         = rc.get_singleton()
menuwidget = menu.get_singleton()
mixer      = mixer.get_singleton()

# Module variable that contains an initialized MPlayer() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MPlayer()
        
    return _singleton


class MPlayer:

    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.start()
        self.mode = None
                         
    def play(self, mode, filename, playlist, repeat=0, mplayer_options=""):

        self.mode   = mode   # setting global var to mode.
        self.repeat = repeat # Repeat playlist setting

        if( (mode == 'video' or mode == 'audio') and
            not os.path.isfile(filename) ):
            osd.clearscreen()
            osd.drawstring('File "%s" not found!' % filename, 30, 280)
            osd.update()
            time.sleep(2.0) 
            menuwidget.refresh()
            # XXX We should really use return more. And this escape should
            # XXX probably be put at start of the function.
            return 0
        
        if mode == 'video':

            # Mplayer command and standard arguments
            mpl = config.MPLAYER_CMD + ' ' + config.MPLAYER_ARGS_MPG
            
            # Add special arguments for the hole playlist from the
            # XML file
            if mplayer_options:
                mpl += (' ' + mplayer_options)
                if DEBUG: print 'options, mpl = "%s"' % mpl

            # Some files needs special arguments to mplayer, they can be
            # put in a <filename>.mplayer options file. The <filename>
            # includes the suffix (.avi, etc)!
            # The arguments in the options file are added at the end of the
            # regular mplayer arguments.
            if os.path.isfile(filename + '.mplayer'):
                mpl += (' ' + open(filename + '.mplayer').read().strip())
                if DEBUG: print 'Read options, mpl = "%s"' % mpl
                
            command = mpl + ' "' + filename + '"'
            
        elif mode == 'dvdnav':
            command = config.MPLAYER_CMD + ' ' + config.MPLAYER_ARGS_DVDNAV

        elif mode == 'vcd':
            mpl = config.MPLAYER_CMD + ' ' + config.MPLAYER_ARGS_VCD
            command = mpl % filename  # Filename is VCD chapter

        # XXX Code to make mplayer play our audio aswell.
        elif mode == 'audio':
            mpl = config.MPLAYER_CMD 
            command = mpl + ' "' + filename + '"'

        else:
            mpl = config.MPLAYER_CMD + ' ' + config.MPLAYER_ARGS_DVD
            command = mpl % filename  # Filename is DVD chapter
            
        self.filename = filename
        self.playlist = playlist

        # XXX Remember to do stuff for selecting major audio device.
        mixer.setPcmVolume(100)
        mixer.setLineinVolume(0)
        mixer.setMicVolume(0)

        # XXX Is this really needed? We need to do different stuff
        # XXX for music GUI
        #osd.clearscreen(color=osd.COL_BLACK)
        #osd.drawstring('mplayer %s "%s"' % (mode, filename), 30, 280,
        #               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
        # osd.update()

        if mode == 'audio':
            self.thread.audioinfo = audioinfo.AudioInfo( filename, 1 )
            self.thread.audioinfo.start = time.time()
            skin.DrawMP3( self.thread.audioinfo ) 
            self.thread.audioinfo.drawall = 0

        self.mplayer_options = mplayer_options

        self.thread.mode    = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        rc.app = self.eventhandler
        
    def stop(self):
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.3)


    def eventhandler(self, event):
        if event == rc.STOP or event == rc.SELECT:
            if self.mode == 'dvdnav':
                self.thread.app.write('S')
            else:
                self.stop()
                rc.app = None
                menuwidget.refresh()
        elif event == rc.MENU:
            self.thread.app.write('M')
        elif event == rc.DISPLAY:
            self.thread.cmd( 'info' )
        elif event == rc.PAUSE or event == rc.PLAY:
            if self.mode == 'audio':
                self.thread.audioinfo.toggle_pause()
            self.thread.cmd('pause')
        elif event == rc.FFWD:
            if self.mode == 'audio':
                # XXX this is kinda silly to hardcode.. let's hope mplayer
                # XXX Doesn't change it's spec soon :)
                self.thread.audioinfo.ffwd( 10 )
            self.thread.cmd('skip_forward')
        elif event == rc.UP:
            if self.mode == 'dvdnav':
                self.thread.app.write('K')
            else:
                if self.mode == 'audio':
                    # XXX this is kinda silly to hardcode.. let's hope mplayer
                    # XXX Doesn't change it's spec soon :)
                    self.thread.audioinfo.ffwd( 60 )
                self.thread.cmd('skip_forward2')
        elif event == rc.REW:
            if self.mode == 'audio':
                # XXX this is kinda silly to hardcode.. let's hope mplayer
                # XXX Doesn't change it's spec soon :)
                self.thread.audioinfo.rwd( 10 )
            self.thread.cmd('skip_back')
        elif event == rc.DOWN:
            if self.mode == 'dvdnav':
                self.thread.app.write('J')
            else:
                if self.mode == 'audio':
                    # XXX this is kinda silly to hardcode.. let's hope mplayer
                    # XXX Doesn't change it's spec soon :)
                    self.thread.audioinfo.rwd( 60 )
                self.thread.cmd('skip_back2')
        elif event == rc.LEFT:
            if self.mode == 'dvdnav':
                self.thread.app.write('H')
            else:
                self.stop()
                if self.playlist == []:
                    rc.app = None
                    menuwidget.refresh()
                else:
                    # Go to the previous movie in the list
                    pos = self.playlist.index(self.filename)
                    pos = (pos-1) % len(self.playlist)
                    filename = self.playlist[pos]
                    self.play(self.mode, filename, self.playlist, self.repeat,\
                              self.mplayer_options)
        elif event == rc.PLAY_END or event == rc.RIGHT:
            if event == rc.RIGHT and self.mode == 'dvdnav':
                self.thread.app.write('L')
            else:
                self.stop()
                if self.playlist == []:
                    rc.app = None
                    menuwidget.refresh()
                else:
                    pos = self.playlist.index(self.filename)
                    last_file = (pos == len(self.playlist)-1)
                
                    # Don't continue if at the end of the list
                    if self.playlist == [] or (last_file and not self.repeat):
                        rc.app = None
                        menuwidget.refresh()
                    else:
                        # Go to the next song in the list
                        pos = (pos+1) % len(self.playlist)
                        filename = self.playlist[pos]
                        self.play( self.mode, filename, self.playlist,
                                   self.repeat, self.mplayer_options )
            
# ======================================================================
class MPlayerApp(childapp.ChildApp):
        
    def kill(self):
        childapp.ChildApp.kill(self, signal.SIGINT)
	osd.update()

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

                self.app = MPlayerApp(self.command)
                
                while self.mode == 'play' and self.app.isAlive():
                    # if DEBUG: print "Still running..."
                    if self.audioinfo: 
                        # if DEBUG: print "Got Audioinfo"
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
        'VOLUMEDOWN'     : '/'
        }
    
    key = mplayerKeys.get(rcCommand, '')

    return key
