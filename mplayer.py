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
# Revision 1.51  2002/11/17 02:30:17  krister
# Re-added the radio station example URL. Fixed a playlist handling bug.
#
# Revision 1.50  2002/11/15 02:49:15  krister
# Added a config option for saving MPlayer output to a logfile.
#
# Revision 1.49  2002/11/14 13:34:31  krister
# Adjust the SDL/DXR3 patch.
#
# Revision 1.48  2002/11/14 03:47:49  krister
# Added Thomas Shueppel's SDL/DXR3 patch.
#
# Revision 1.47  2002/11/13 14:34:21  krister
# Fixed a bug in music playing (the file type was mistaken for video for songs without an absolute path) by changing the way file suffixes are handled. The format of suffixes in freevo_config.py changed, local_conf.py must be updated!
#
# Revision 1.46  2002/11/09 17:36:31  dischi
# Some stuff to work with the changes in datatypes and movie_config.
#
# Also there is a seek to position code. Since the -ss flag from mplayer
# is way to bad (seek to position 20:00 jumps to 35:xxx), I implemented
# a small work around. Freevo moves forward in the video until we are
# ahead for the start_position. Than we go backwards until it fits. This
# is a bad hack (TM) and should be removed when seek to position works in
# mplayer.
#
# Revision 1.45  2002/11/08 21:28:20  dischi
# Added support for a movie config dialog. Only usable for dvd right now.
# See mplayer-devel list for details.
#
# Revision 1.44  2002/10/31 21:10:11  dischi
# mplayer.py doesn't believe the type for a file anymore and checks
# the type by parsing config.SUFFIX_AUDIO_FILES. This had to be done
# because there can be mixed playlists now.
#
# Revision 1.43  2002/10/28 21:52:20  dischi
# Fixed a bug that DrawMP3 is called when we start a movie and
# prev. listened to music and it stopped by itself (rc.PLAY_END).
#
# Revision 1.42  2002/10/24 05:27:10  outlyer
# Updated audioinfo to use new ID3v2, ID3v1 support. Much cleaner, and uses
# the eyed3 library included. Notable changes:
#
# o Invalid audio files do not cause a crash, both broken oggs and broken mp3s
#    now pop up an "Invalid Audio File" message (also if you just rename a non-
#    audiofile to *.mp3 or *.ogg.
# o Full ID3v2.3 and 2.4 support, v2.2 is not supported, but gracefully falls
#    back to v1.1, if no tags are found, behaviour is normal.
# o Now survives the crash reported by a user
# o There are self.valid and self.trackof variables in audioinfo, to store the
#    validity of the file (passing the header checks for Ogg and MP3) and to
#    store the total numbers of tracks in an album as allowed by the v2.x spec.
# o I'll be updating the skin as well, with support for self.trackof, and to
#    truncate the text in album, artist and title, since they can now be
#    significantly longer than v1.1 and can (and have) run off the screen.
#
# Revision 1.41  2002/10/23 06:58:03  krister
# Added OSD stop/start patch from Michael Hunold.
#
# Revision 1.40  2002/10/21 05:09:50  krister
# Started adding support for playing network audio files (i.e. radio stations). Added one station in freevo_config.py, seems to work. Need to fix audioinfo.py with title, time etc. Need to look at using xml files for this too.
#
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
import fnmatch

# RegExp
import re

import movie_config
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
                         
    def play(self, mode, file, playlist, repeat=0, start_time = 0):

        # The playlist must be a list type
        if playlist == None:
            playlist = []
            
        filename = file
        if isinstance(filename, FileInformation):
            mplayer_options = file.mplayer_options
            mode = file.mode
            filename = filename.file
        else:
            mplayer_options = ''

        # Is the file streamed over the network?
        if filename.find('://') != -1:
            # Yes, trust the given mode
            network_play = 1
        else:
            network_play = 0
            
            # Since we have mixed playlists don't trust the given mode
            if (not mode) or (mode == 'video') or (mode == 'audio'):
                # Set to video if it doesn't match an audio suffix
                if util.match_suffix(filename, config.SUFFIX_AUDIO_FILES):
                    mode = 'audio'
                else:
                    mode = 'video'
            
        self.mode = mode   # setting global var to mode.
        self.repeat = repeat # Repeat playlist setting

        if DEBUG:
            print 'MPlayer.play(): mode=%s, filename=%s' % (mode, filename)

        if (((mode == 'video') or (mode == 'audio')) and
            not os.path.isfile(filename) and not network_play):
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

        # XXX find a way to enable this for AVIs with ac3, too
        if (mode == 'dvdnav' or mode == 'dvd' or os.path.splitext(filename)[1] == '.vob')\
           and config.MPLAYER_AO_HWAC3_DEV:
            mpl += ' -ao %s -ac hwac3' % config.MPLAYER_AO_HWAC3_DEV
        else:
            mpl += ' -ao %s' % config.MPLAYER_AO_DEV

        if mode == 'video':

            # Mplayer command and standard arguments
            mpl += (' ' + config.MPLAYER_ARGS_MPG + ' -v -vo ' + config.MPLAYER_VO_DEV)
            
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
            if not network_play:
                demux = ' %s ' % get_demuxer(filename)
            else:
                # Don't include demuxer for network files
                demux = ''

            command = '%s -vo null %s "%s"' % (mpl, demux, filename)
            
        elif mode == 'dvd':
            mpl += (' ' + config.MPLAYER_ARGS_DVD + ' -v -alang ' + config.DVD_LANG_PREF +
                    ' -vo ' + config.MPLAYER_VO_DEV)
            # XXX this can be set by the config menu
            # if config.DVD_SUBTITLE_PREF:
            #     mpl += (' -slang ' + config.DVD_SUBTITLE_PREF)
            command = mpl % str(filename)  # Filename is DVD chapter
            
        else:
            print "Don't know what do play!"
            print "What is:      " + str(filename)
            print "What is mode: " + mode
            print "What is:      " + mpl
            return

        # Add special arguments
        if mplayer_options:
            if mplayer_options[0]:
                command += ' ' + mplayer_options[0]
            if mplayer_options[1]:
                command += ' ' + mplayer_options[1].to_string()
            if mplayer_options[2]:
                command += ' ' + mplayer_options[2]
                mplayer_options[2] = ""
                
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
            self.thread.audioinfo = audioinfo.AudioInfo(filename, 1)
	    print "Valid: " + str(self.thread.audioinfo.valid)
	    if self.thread.audioinfo.valid:
                self.thread.audioinfo.start = time.time()
                skin.DrawMP3(self.thread.audioinfo) 
                self.thread.audioinfo.drawall = 0
	    else:
	        # Invalid file, show an error and survive.
		skin.PopupBox('Invalid audio file')
		time.sleep(3.0)
		menuwidget.refresh()
		return
        else:
            # clear the screen for mplayer
            osd.clearscreen(color=osd.COL_BLACK)
            osd.update()

        self.thread.play_mode = self.mode

        if DEBUG:
            print 'MPlayer.play(): Starting thread, cmd=%s' % command
            
        self.thread.mode    = 'play'
        if mplayer_options:
            self.thread.mplayer_config = mplayer_options[1]
        else:
            self.thread.mplayer_config = None
        self.thread.start_time = start_time
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
            self.thread.audioinfo = None
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
            if self.mode == 'dvdnav':
                self.thread.app.write('M')
            elif self.mode == 'dvd':
                mpinfo = self.thread.app.mpinfo
                self.stop()
                rc.app = None
                movie_config.config_main_menu(self.mode, self.file, self.playlist,
                                              self.repeat, mpinfo)

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
    def __init__(self, app, mpinfo):
        if mpinfo:
            self.mpinfo = mpinfo
        else:
            self.mpinfo = movie_config.MplayerMovieInfo()
        self.start_time = 0
        self.seek_mode = "forward"
        childapp.ChildApp.__init__(self, app)


    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)

        # XXX Krister testcode for proper X11 video
        if DEBUG: print 'Killing mplayer'
        os.system('killall -9 freevo_xwin 2&> /dev/null')
        os.system('rm -f /tmp/freevo.wid')


    def stdout_cb(self, str):

        if config.MPLAYER_DEBUG:
            fd = open('./mplayer_stdout.log', 'a')
            fd.write(str + '\n')
            fd.close()
                     
        if str.find("A:") == 0:
            # seek for the right position on startup
            #
            # XXX HACK: seek 10, 1 minute or 10 seconds until we
            # XXX reached to needed position. Than go back 10 seconds
            # XXX until we are _behind_ the start_time
            if self.start_time:
                m = re.compile("^A[: -]*([0-9]+)\.").match(str)

                if m and self.seek_mode == "forward":
                    if int(m.group(1)) + 60 <= self.start_time:
                        str = mplayerKey('UP')
                        self.write(str)
                    elif int(m.group(1)) + 10 <= self.start_time:
                        str = mplayerKey('RIGHT')
                        self.write(str)
                    else:
                        self.seek_mode = "backward"
                        
                if m and self.seek_mode == "backward":
                    if int(m.group(1)) > self.start_time:
                        str = mplayerKey('LEFT')
                        self.write(str)
                    else:
                        self.seek_mode = "forward"
                        self.start_time = 0

            else:
                self.mpinfo.time = str

        # this is the first start of the movie, parse infos
        elif not self.mpinfo.time:
            self.mpinfo.parse(str)


    def stderr_cb(self, str):

        if config.MPLAYER_DEBUG:
            fd = open('./mplayer_stderr.log', 'a')
            fd.write(str + '\n')
            fd.close()
                     

# ======================================================================
class MPlayer_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.play_mode = ''
        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None
        self.audioinfo = None              # Added to enable update of GUI
        self.mplayer_config = None
        self.start_time = 0
        
    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'play':

                # The DXR3 device cannot be shared between our SDL session
                # and MPlayer.
                if (osd.sdl_driver == 'dxr3' and self.play_mode != 'audio'):
                    if DEBUG:
		        print "Stopping Display for Video Playback on DXR3"
                    osd.stopdisplay()
                
                if DEBUG:
                    print 'MPlayer_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = MPlayerApp(self.command, self.mplayer_config)

                # XXX Bad hack: store the value to seek to in the childapp
                # XXX to seek forward to this position
                self.app.start_time = self.start_time
                self.start_time = 0
                while self.mode == 'play' and self.app.isAlive():
                    # if DEBUG: print "Still running..."
                    if self.audioinfo: 
                        if not self.audioinfo.pause:
                            self.audioinfo.draw()        
                    time.sleep(0.1)

                self.app.kill()

                # Ok, we can use the OSD again.
                if osd.sdl_driver == 'dxr3' and self.play_mode != 'audio':
                    osd.restartdisplay()
		    osd.update()
		    print "Display back online"

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
