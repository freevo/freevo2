#
# mplayer.py
#
# This is the Freevo MPlayer module. 
#

import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading, signal

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


    def play(self, mode, filename, playlist, repeat=0):

        # Repeat playlist setting
        self.repeat = repeat
        
        if mode == 'video':

            # Mplayer command and standard arguments
            mpl = config.MPLAYER_CMD + ' ' + config.MPLAYER_ARGS_MPG
            
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
        else:
            mpl = config.MPLAYER_CMD + ' ' + config.MPLAYER_ARGS_DVD
            command = mpl % filename  # Filename is DVD chapter
            
        self.filename = filename
        self.playlist = playlist
        self.mode = mode
        
        if mode == 'video' and not os.path.isfile(filename):   # XXX Add symlinks
            osd.clearscreen()
            osd.drawstring('xxx', 'File "%s" not found!' % filename, 30, 280)
            time.sleep(2.0)
            menuwidget.refresh()
        else:
            mixer.setPcmVolume(100)
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)

            osd.clearscreen(color=osd.COL_BLACK)
            osd.drawstring('xxx', 'mplayer %s "%s"' % (mode, filename), 30, 280,
                           fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
            self.thread.mode = 'play'
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
            self.thread.cmd('info')
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
        elif event == rc.RIGHT:
            if self.mode == 'dvdnav':
                self.thread.app.write('L')
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
                    self.play(self.mode, filename, self.playlist)
        elif event == rc.PLAY_END or event == rc.LEFT:
            if event == rc.LEFT and self.mode == 'dvdnav':
                self.thread.app.write('H')
            else:
                self.stop()
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
                    self.play(self.mode, filename, self.playlist)
            

class MPlayerApp(childapp.ChildApp):

    def kill(self):
        
        childapp.ChildApp.kill(self, signal.SIGINT)
        
        
        
class MPlayer_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.mode = 'idle'
        self.mode_flag = threading.Event()
        self.command = ''
        self.app = None


    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
            elif self.mode == 'play':

                self.app = MPlayerApp(self.command)
                
                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                self.app.kill()

                if self.mode == 'play':
                    rc.post_event(rc.PLAY_END)
                self.mode = 'idle'
            else:
                self.mode = 'idle'


    def cmd(self, command):
        str = ''
        if command == 'pause':
            str = mplayerKey('PAUSE')
        elif command == 'stop':
            str = mplayerKey('STOP')
        elif command == 'info':
            str = mplayerKey('INFO')
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

        self.app.write(str)


#
# Translate an abstract remote control command to an mplayer
# command key
#
def mplayerKey(rcCommand):
    mplayerKeys = { 'NONE'           : '',
                    'OK'             : 'q',
                    'STOP'           : 'q',
                    'PLAY'           : ' ',
                    'PAUSE'          : ' ',
                    'VOLUMEUP'       : '*',
                    'VOLUMEDOWN'     : '/',
                    'INFO'           : 'o',
                    'LEFT'           : '\x1bOD',
                    'RIGHT'          : '\x1bOC',
                    'UP'             : '\x1bOA',
                    'DOWN'           : '\x1bOB',
                    'PAGEUP'         : '\x1b[5~',
                    'PAGEDOWN'       : '\x1b[6~',
                    'KEY_1'          : '+',
                    'KEY_7'          : '-'
                    }
    
    key = mplayerKeys.get(rcCommand, '')

    return key
