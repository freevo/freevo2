#if 0 /*
# -----------------------------------------------------------------------
# xmmsaudioplayer.py - Play music using XMMS
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/11/23 19:24:02  dischi
# New version of the code cleanup, not working right now, wait for more
# checkins in some minutes please
#
# Revision 1.5  2002/11/10 07:29:22  krister
# Added Alex Polite's bugfix patch.
#
# Revision 1.4  2002/10/21 02:31:38  krister
# Set DEBUG = config.DEBUG.
#
# Revision 1.3  2002/10/17 04:16:16  krister
# Changed the 'nice' command so that it is built into runapp instead. Made default prio -20.
#
# Revision 1.2  2002/10/16 02:49:32  krister
# Changed to use config.MAX_VOLUME for when resetting the volume to max.
#
# Revision 1.1  2002/10/02 02:40:56  krister
# Applied Alex Polite's patch for using XMMS instead of MPlayer for music playing and visualization.
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
import threading
import os
import signal
import time
import os.path

import menu       # The menu widget class
import mixer      # Controls the volumes for playback and recording
import rc         # The RemoteControl class.
import config
import childapp
import osd
import exceptions
import skin

# This is an external package
try:
    import xmms
except ImportError:
    print
    print
    print 'pyxmms is not (properly?) installed!'
    print
    sys.exit(1)
    

DEBUG = config.DEBUG


# Setting up the default objects:
class Globals:
    pass

globals = Globals()

osd =        globals.osd        = osd.get_singleton()
rc =         globals.rc         = rc.get_singleton()
menuwidget = globals.menuwidget = menu.get_singleton()
mixer =      globals.mixer      = mixer.get_singleton()
skin =       globals.skin       = skin.get_singleton()


# Setting up some constants

# Playermodes
class Constants:
    pass

constants = Constants()

constants.videomode ='video'
constants.audiomode ='audio'
constants.playmode  ='play'
constants.idlemode  ='idle'
constants.stopmode  ='stop'

# Constants pertaining to unittests
constants.profilestatsfile = "/tmp/stats"


class NotImplementedError(exceptions.Exception):
    pass

# Module variable that contains an initialized Xmms() object
class AbstractAudioPlayerThread(threading.Thread):
    def run(self):
        raise  NotImplementedError


class Singleton:
    """
    Any class that needs singleton behavior should inherit Singleton.
    """
    _singleton = None
    
    def get_singleton(cls):
        if cls._singleton == None:
            cls._singleton = cls()
        return cls._singleton

    get_singleton = classmethod(get_singleton)
    
class AbstractAudioPlayer(Singleton):

    #Override in subclass with something like AudioplayerThread
    ThreadClass = NotImplementedError



    
    def play(self, mode, filename, playlist, repeat=0):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def eventhandler(self, event):
        raise NotImplementedError

    def reset_thread(self):
        self.thread = self.__class__.ThreadClass(self)
        self.thread.start()
        self.mode = None

    def file_not_found(self, filename):
	if DEBUG:
	    print "xmms file_not_found %s " % (filename,)
	if xmms.is_running():
	    globals.rc.post_event(globals.rc.RIGHT)
	else:
	    skin.PopupBox('File "%s" not found!' % filename)
	    time.sleep(3.0)
	    menuwidget.refresh()

    def set_mixer_levels(self):
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


        

class AbstractAudioPlayerApp(childapp.ChildApp):
    def kill(self, sig):
        raise NotImplementedError

    
class AudioPlayerApp(AbstractAudioPlayerApp):
    def kill(self, sig=signal.SIGKILL):
        childapp.ChildApp.kill(self, sig)
        globals.osd.update()

class AudioPlayerThread(AbstractAudioPlayerThread):

    AppClass = AudioPlayerApp

    def __init__(self, audioplayer):
        threading.Thread.__init__(self)
        self.mode      = constants.idlemode
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None
        self.reset_alive()
        self.audioplayer = audioplayer
        
    def _set_app(self):
        if self.app == None:
            self.app = self.__class__.AppClass(self.command)
        
    def reset_alive(self):
        self.alive_last = 0
        self.alive_stop = 0
        
    def run(self):
        while 1:
            if self.mode == constants.idlemode:
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == constants.playmode:
                self._set_app()
                self.audioplayer.load_and_play()
                while (self.mode == constants.playmode) and self._alive():
                    time.sleep(0.5)

                #self.app.kill()
                if self.mode == constants.playmode:
                    globals.rc.post_event(globals.rc.PLAY_END)
                self.mode = constants.idlemode
            else:
                self.mode = constants.idlemode

    def _alive(self):
        playing = xmms.is_playing()
        self.alive_stop = not playing and self.alive_last
        self.alive_last = playing
        return not self.alive_stop

        
    def cmd(self, command):
        if command == 'pause':
            xmms.pause()
        elif command == 'stop':
            xmms.stop()
        else:
            pass

class AudioPlayer(AbstractAudioPlayer):

    ThreadClass = AudioPlayerThread
    
    def __init__(self):
        self.reset_thread()

    def _return_to_menu(self):
        self.thread.app.kill()
        self.thread.app = None
        globals.rc.app = None
        globals.menuwidget.refresh()
        
    def eventhandler(self, event):
        if event == globals.rc.STOP:
            self.stop ()
            self._return_to_menu()

        if event == globals.rc.SELECT:
            self.stop ()
            self._return_to_menu()

        elif event == globals.rc.PAUSE:
            self.thread.cmd('pause')
            
        elif event == globals.rc.LEFT:
            self.stop()
            #if the playlist is empty go back to menu
            if self.playlist == []:
                self._return_to_menu()
            #if the playlist is not empty go to the previous file in the list
            else:
                pos = self.playlist.index(self.filename)
                pos = (pos-1) % len(self.playlist)
                filename = self.playlist[pos]
                self.play(self.mode, filename, self.playlist, self.repeat)

        elif event == globals.rc.PLAY_END or event == globals.rc.RIGHT:
            self.stop()

            #if the playlist is empty go back to menu
            if self.playlist == []:
                self._return_to_menu()
            else:
                pos = self.playlist.index(self.filename)
                last_file = (pos == len(self.playlist)-1)
                if DEBUG:
		    print "xmms play pos: %s last_file: %s " % (pos,last_file)
                # Don't continue if at the end of the list
                if last_file and not self.repeat:
                    self._return_to_menu()
                else:
                    # Go to the next song in the list

                    pos = (pos+1) % len(self.playlist)
                    filename = self.playlist[pos]
		    if DEBUG:
			print "xmms goto next song in list pos: %s filename: %s " % (pos,filename)
                    self.play( self.mode, filename, self.playlist, self.repeat)
        elif event == globals.rc.VOLUP:
            pass


    def build_play_command(self):
        cmd = '--prio=%s %s' % (config.XMMS_NICE,
                                config.XMMS_CMD)

        return cmd
    
        
    def play(self, mode, filename, playlist, repeat=1):

        self.filename = filename
        self.quoted_filename = '"' + self.filename + '"'
        self.playlist = playlist
        if not os.path.isfile(filename):
	    self.file_not_found(filename)
	else:
        
	    self.mode = mode # setting global var to mode.
	    self.repeat = repeat # Repeat playlist setting
	    
	    globals.skin.PopupBox("Lanching xmms.")
	    self.set_mixer_levels()
        
	    self.thread.mode  = constants.playmode
	    self.thread.reset_alive()
	    self.thread.command = self.build_play_command()
	    self.thread.mode_flag.set()
	    globals.rc.app = self.eventhandler


    def load_and_play(self):
	timeout = 10.0
	counter = 0.0
	increment = 0.1
	while 1:
	    if xmms.is_running():
		if DEBUG:
		    print "xmms is running"
		xmms.play_files((self.filename,))
		xmms.main_win_toggle(0)
		break
	    elif counter >= timeout:
		if DEBUG:
		    print "xmms timeout"
		menuwidget.refresh()
		skin.PopupBox("Timed launching xmms.")
		time.sleep(3)
		menuwidget.refresh()
		break
	    else:
		if DEBUG:
		    print "xmms waiting to come up", counter
		time.sleep(increment)
		counter += increment
		
		



    def stop(self):
        self.thread.mode = constants.stopmode
        self.thread.mode_flag.set()
        self.thread.cmd('stop')
        while self.thread.mode == constants.stopmode:
            time.sleep(0.1)
