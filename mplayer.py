#if 0
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer module. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes:    
# Todo:     
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.24  2002/08/08 03:15:57  krister
# Tidied up some code.
#
# Revision 1.23  2002/08/05 00:50:33  tfmalt
# o Split eventhandler into eventhandler_audio and eventhandler. This should
#   make the code easier to maintain.
# o Added start of eventhandling which manipulates the audio GUI (draw a
#   volume meter when changing the volume etc.)
#
# Revision 1.22  2002/08/05 00:33:37  outlyer
# Removed some debugging code I put in.
#
# Revision 1.21  2002/08/05 00:30:05  outlyer
# Fixed the bug with mplayer detecting MP3 files as Encrypted VOBS. We now
# force the demuxer for audio files, thereby fixing half of my MP3 collection.
# Currently we only force demuxers for OGG and MP3 files, but check "demuxer.h"
# in the mplayer source for a list of others. I don't believe they are
# necessary though, as only MP3 has so many, many encoders with varying
# output.
#
# While this alleviates the "urgency" of my plugin question, I still think
# we should come up with a system of some kind.
#
# Revision 1.20  2002/08/04 16:49:20  dischi
# DISPLAY toggles the mplayer OSD
#
# Revision 1.19  2002/08/03 18:55:44  outlyer
# Last change to config file :)
#
# o You can now set the priority of the mplayer process via a nice setting
# o This involves two lines in the config file: NICE and MPLAYER_NICE for the
# 	path to 'nice' and the actual numeric priority where '-10' is the
# 	default (high priority) set it to 0 for normal priority or +10 for
# 	low priority.
#
# Revision 1.18  2002/08/03 18:15:22  dischi
# o added the patch from Thomas Malt for better audio control
# o added support for the new freevo_config.py file
#
# Revision 1.17  2002/07/31 08:13:22  dischi
# make screen black before mplayer starts in case mplayer doesn't cover
# the hole screen
#
# Revision 1.15  2002/07/29 18:13:13  outlyer
# Fixed "deja vu" of audio progressbar when playing movies after playing mp3s.
#
# Revision 1.14  2002/07/29 05:24:35  outlyer
# Lots and lots of changes for new mplayer-based audio playing code.
# o You'll need to modify your config file, as well as setup the new mplayer
#   module by editing main.py
# o This change includes Ogg Support, but that requires the ogg.vorbis
#   module. If you don't want it, just don't install ogg.vorbis :)
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
# -----------------------------------------------------------------------
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

def get_demuxer(filename):
    DEMUXER_MP3 = 17
    DEMUXER_OGG = 18
    rest, extension	= os.path.splitext(filename)
    if string.lower(extension) == '.mp3':
	return "-demuxer " + str(DEMUXER_MP3)
    if string.lower(extension) == '.ogg':
	return "-demuxer " + str(DEMUXER_OGG)
    else:
    	return ''


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
       
        # build mplayer command
        mpl = (config.NICE + " -" + config.MPLAYER_NICE + " " +
               config.MPLAYER_CMD + ' -vo ' + config.MPLAYER_VO_DEV + 
               ' -ao ' +  config.MPLAYER_AO_DEV + ' ' +
               config.MPLAYER_ARGS_DEF)

        if mode == 'video':

            # Mplayer command and standard arguments
            mpl += (' ' + config.MPLAYER_ARGS_MPG)
            
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
            mpl += (' ' + config.MPLAYER_ARGS_DVDNAV)
            command = mpl


        elif mode == 'vcd':
            mpl += (' ' + config.MPLAYER_ARGS_VCD + ' -alang ' + config.DVD_LANG_PREF)
            if config.DVD_SUBTITLE_PREF:
                mpl += (' -slang ' + config.DVD_SUBTITLE_PREF)
            command = mpl % filename  # Filename is VCD chapter


        elif mode == 'audio':
            command = mpl + " " + get_demuxer(filename) + ' "' + filename + '"'

        else:
            mpl += (' ' + config.MPLAYER_ARGS_DVD + ' -alang ' + config.DVD_LANG_PREF)
            if config.DVD_SUBTITLE_PREF:
                mpl += (' -slang ' + config.DVD_SUBTITLE_PREF)
            print "What is:      " + str(filename)
            print "What is mode: " + mode
            print "What is:      " + mpl
            command = mpl % str(filename)  # Filename is DVD chapter
            


        self.filename = filename 
        self.playlist = playlist

        # XXX A better place for the major part of this code would be
        # XXX mixer.py
        if config.CONTROL_ALL_AUDIO:
            mixer.setLineinVolume( 0 )
            mixer.setMicVolume( 0 )
            if( config.MAJOR_AUDIO_CTRL == 'VOL' ):
                mixer.setPcmVolume( 100 )
            elif( config.MAJOR_AUDIO_CTRL == 'PCM' ):
                mixer.setMainVolume( 100 )
                
        mixer.setIgainVolume( 0 ) # SB Live input from TV Card.
        # This should _really_ be set to zero when playing other audio.

        if mode == 'audio':
            self.thread.audioinfo = audioinfo.AudioInfo( filename, 1 )
            self.thread.audioinfo.start = time.time()
            skin.DrawMP3( self.thread.audioinfo ) 
            self.thread.audioinfo.drawall = 0
        else:
            # clear the screen for mplayer
            osd.clearscreen(color=osd.COL_BLACK)
            osd.update()

            
        self.mplayer_options = mplayer_options

        self.thread.mode    = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        if(mode == 'audio'):
            rc.app = self.eventhandler_audio
        else:
            rc.app = self.eventhandler
        
    def stop(self):
        # self.thread.audioinfo = None
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.3)


    def eventhandler_audio(self, event):
        if self.mode != 'audio':
            # XXX It might be good to throw exception here.
            if DEBUG: print "Oops.. got not audio mode in audio eventhandler"
            return 0
        
        if event == rc.STOP or event == rc.SELECT:
            # XXX Not sure if I want stop and select to be the same.
            self.thread.audioinfo = None
            self.stop ()
            rc.app = None
            menuwidget.refresh()
        elif event == rc.MENU:
            # XXX What to do with audio on menu
            pass
        elif event == rc.DISPLAY:
            # XXX What to do? 
            pass
        elif event == rc.PAUSE:
            self.thread.audioinfo.toggle_pause()
            self.thread.cmd('pause')
        elif event == rc.FFWD:
            # XXX this is kinda silly to hardcode.. let's hope mplayer
            # XXX Doesn't change it's spec soon :)
            self.thread.cmd('skip_forward')
            self.thread.audioinfo.ffwd(10)
        elif event == rc.UP:
            # XXX this is kinda silly to hardcode.. let's hope mplayer
            # XXX Doesn't change it's spec soon :)
            self.thread.cmd('skip_forward2')
            self.thread.audioinfo.ffwd( 60 )
        elif event == rc.REW:
            # XXX this is kinda silly to hardcode.. let's hope mplayer
            # XXX Doesn't change it's spec soon :)
            self.thread.audioinfo.rwd( 10 )
            self.thread.cmd('skip_back')
        elif event == rc.DOWN:
            # XXX this is kinda silly to hardcode.. let's hope mplayer
            # XXX Doesn't change it's spec soon :)
            self.thread.audioinfo.rwd( 60 )
            self.thread.cmd('skip_back2')
        elif event == rc.LEFT:
            self.stop()
            if self.playlist == []:
                rc.app = None
                menuwidget.refresh()
            else:
                # Go to the previous movie in the list
                pos = self.playlist.index(self.filename)
                pos = (pos-1) % len(self.playlist)
                filename = self.playlist[pos]
                self.play(self.mode, filename, self.playlist, self.repeat,
                          self.mplayer_options)
        elif event == rc.PLAY_END or event == rc.RIGHT:
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
        elif event == rc.VOLUP:
            print "Got VOLUP in mplayer!"
            # osd.popup_box('Volume shall come here')
            # osd.update()
            # time.sleep(1.0)
            # self.thread.audioinfo.drawall = 1
            # time.sleep(0.2)
            # self.thread.audioinfo.drawall = 0
                   
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
            self.thread.cmd('pause')
        elif event == rc.FFWD:
            self.thread.cmd('skip_forward')
        elif event == rc.UP:
            if self.mode == 'dvdnav':
                self.thread.app.write('K')
            else:
                self.thread.cmd('skip_forward2')
        elif event == rc.REW:
            self.thread.cmd('skip_back')
        elif event == rc.DOWN:
            if self.mode == 'dvdnav':
                self.thread.app.write('J')
            else:
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
