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
# Revision 1.39  2002/10/21 02:31:38  krister
# Set DEBUG = config.DEBUG.
#
# Revision 1.38  2002/10/17 04:16:16  krister
# Changed the 'nice' command so that it is built into runapp instead. Made default prio -20.
#
# Revision 1.37  2002/10/16 02:49:33  krister
# Changed to use config.MAX_VOLUME for when resetting the volume to max.
#
# Revision 1.36  2002/10/13 05:41:17  outlyer
# Fixed another drawstring call that should be skin.PopupBox()
#
# Revision 1.35  2002/10/06 14:58:51  dischi
# Lots of changes:
# o removed some old cvs log messages
# o some classes without member functions are in datatypes.py
# o movie_xml.parse now returns an object of MovieInformation instead of
#   a long list
# o mplayer_options now works better for options on cd/dvd/vcd
# o you can disable -wid usage
# o mplayer can play movies as strings or as FileInformation objects with
#   mplayer_options
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

from datatypes import *

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

    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.start()
        self.mode = None
                         
    def play(self, mode, file, playlist, repeat=0):

        self.mode   = mode   # setting global var to mode.
        self.repeat = repeat # Repeat playlist setting
        mplayer_options = ''
        
        filename = file
        if isinstance(filename, FileInformation):
            mplayer_options = file.mplayer_options
            mode = file.mode
            filename = filename.file
            
        if DEBUG:
            print 'MPlayer.play(): mode=%s, filename=%s' % (mode, filename)
            

        if (((mode == 'video') or (mode == 'audio')) and
            not os.path.isfile(filename)):
	    skin.PopupBox('%s\nnot found!' % filename)
            time.sleep(2.0) 
            menuwidget.refresh()
            # XXX We should really use return more. And this escape should
            # XXX probably be put at start of the function.
            return 0
       
        # Build the MPlayer command
        mpl = '--prio=%s %s %s' % (config.MPLAYER_NICE,
                                   config.MPLAYER_CMD,
                                   config.MPLAYER_ARGS_DEF)

        # XXX find a way to enable this for AVIs with ac3, too
        if (mode == 'dvdnav' or mode == 'dvd' or os.path.splitext(filename)[1] == '.vob')\
           and config.MPLAYER_AO_HWAC3_DEV:
            mpl += ' -ao %s -ac hwac3' % config.MPLAYER_AO_HWAC3_DEV
        else:
            mpl += ' -ao %s' % config.MPLAYER_AO_DEV

        if mode == 'video':

            # Mplayer command and standard arguments
            mpl += (' ' + config.MPLAYER_ARGS_MPG + ' -vo ' + config.MPLAYER_VO_DEV)
            
            # XXX Some testcode by Krister:
            if os.path.isfile('./freevo_xwin') and osd.sdl_driver == 'x11' and \
               config.MPLAYER_USE_WID:
                if DEBUG: print 'Got freevo_xwin and x11'
                os.system('rm -f /tmp/freevo.wid')
                os.system('./freevo_xwin  0 0 %s %s > /tmp/freevo.wid &' %
                          (osd.width, osd.height))
                time.sleep(1)
                if os.path.isfile('/tmp/freevo.wid'):
                    if DEBUG: print 'Got freevo.wid'
                    try:
                        wid = int(open('/tmp/freevo.wid').read().strip(), 16)
                        mpl += ' -wid 0x%08x -xy %s -monitoraspect 4:3' % (wid, osd.width)
                        if DEBUG: print 'Got WID = 0x%08x' % wid
                    except:
                        pass
                
            command = mpl + ' "' + filename + '"'
            

        elif mode == 'dvdnav':
            mpl += (' ' + config.MPLAYER_ARGS_DVDNAV + ' -vo ' + config.MPLAYER_VO_DEV)
            command = mpl


        elif mode == 'vcd':
            mpl += (' ' + config.MPLAYER_ARGS_VCD + ' -alang ' + config.DVD_LANG_PREF +
                    ' -vo ' + config.MPLAYER_VO_DEV)
            if config.DVD_SUBTITLE_PREF:
                mpl += (' -slang ' + config.DVD_SUBTITLE_PREF)
            command = mpl % filename  # Filename is VCD chapter


        elif mode == 'audio':
            command = (mpl + " " + '-vo null ' + get_demuxer(filename) +
                       ' "' + filename + '"')

        elif mode == 'dvd':
            mpl += (' ' + config.MPLAYER_ARGS_DVD + ' -alang ' + config.DVD_LANG_PREF +
                    ' -vo ' + config.MPLAYER_VO_DEV)
            if config.DVD_SUBTITLE_PREF:
                mpl += (' -slang ' + config.DVD_SUBTITLE_PREF)
            command = mpl % str(filename)  # Filename is DVD chapter
            
        else:
            print "Don't know what do play!"
            print "What is:      " + str(filename)
            print "What is mode: " + mode
            print "What is:      " + mpl
            return

        # Add special arguments
        if mplayer_options:
            command += ' ' + mplayer_options

        self.file = file
        self.playlist = playlist

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

        if mode == 'audio':
            self.thread.audioinfo = audioinfo.AudioInfo( filename, 1 )
            self.thread.audioinfo.start = time.time()
            skin.DrawMP3( self.thread.audioinfo ) 
            self.thread.audioinfo.drawall = 0
        else:
            # clear the screen for mplayer
            osd.clearscreen(color=osd.COL_BLACK)
            osd.update()

            
        if DEBUG:
            print 'MPlayer.play(): Starting thread, cmd=%s' % command
            
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
        
        if event == rc.EXIT or event == rc.STOP or event == rc.SELECT:
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
                pos = self.playlist.index(self.file)
                pos = (pos-1) % len(self.playlist)
                file = self.playlist[pos]
                self.play(self.mode, file, self.playlist, self.repeat)
        elif event == rc.PLAY_END or event == rc.RIGHT:
            self.stop()
            if self.playlist == []:
                rc.app = None
                menuwidget.refresh()
            else:
                pos = self.playlist.index(self.file)
                last_file = (pos == len(self.playlist)-1)
                
                # Don't continue if at the end of the list
                if self.playlist == [] or (last_file and not self.repeat):
                    rc.app = None
                    menuwidget.refresh()
                else:
                    # Go to the next song in the list
                    pos = (pos+1) % len(self.playlist)
                    file = self.playlist[pos]
                    self.play( self.mode, file, self.playlist, self.repeat)
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
                    pos = self.playlist.index(self.file)
                    pos = (pos-1) % len(self.playlist)
                    file = self.playlist[pos]
                    self.play(self.mode, file, self.playlist, self.repeat)

        elif event == rc.PLAY_END or event == rc.RIGHT:
            if event == rc.RIGHT and self.mode == 'dvdnav':
                self.thread.app.write('L')
            else:
                self.stop()
                if self.playlist == []:
                    rc.app = None
                    menuwidget.refresh()
                else:
                    pos = self.playlist.index(self.file)
                    last_file = (pos == len(self.playlist)-1)
                
                    # Don't continue if at the end of the list
                    if self.playlist == [] or (last_file and not self.repeat):
                        rc.app = None
                        menuwidget.refresh()
                    else:
                        # Go to the next song in the list
                        pos = (pos+1) % len(self.playlist)
                        filename = self.playlist[pos]
                        self.play( self.mode, filename, self.playlist, self.repeat)
            
# ======================================================================
class MPlayerApp(childapp.ChildApp):
        
    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)

        osd.update()  # XXX WTF? /Krister
        
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


# Test code
if __name__ == '__main__':
    player = get_singleton()

    player.play('audio', sys.argv[1], None)
