#
# mp3.py
#
# This is the Freevo MP3 module. 
#
# $Id$

import sys
import random
import time, os, glob, imghdr
import string, popen2, fcntl, select, struct
import threading

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# Handle child applications
import childapp

# The menu widget class
import menu

# The skin class
import skin

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# MP3 ID tags
from mp3_id3 import *

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

# Info about currently playing song
mp3info = None

# Module variable that contains an initialized MPG123() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MPG123()
        
    return _singleton


class MP3Info:

    def __init__(self):
        self.drawall = 0
        self.filename = ''
        self.id3 = None
        self.length = 0
        self.elapsed = 0
        self.remain = 0
        self.done = 0.0
        self.image = ''
    

class MPG123:

    def __init__(self):
        self.thread = MPG123_Thread()
        self.thread.start()
        

    def play(self, filename, playlist, repeat=0):

        global mp3info
        mp3info = MP3Info()
        
        # Repeat playlist setting
        self.repeat = repeat
        
        self.filename = filename
        self.playlist = playlist
        
        if not os.path.isfile(filename):
            osd.clearscreen(0xffffff)
            osd.drawstring('File "%s" not found!' % filename, 30, 280)
            time.sleep(2.0)
            menuwidget.refresh()
        else:

	    # Get cover.png from current directory
	    cover_logo = os.path.dirname(filename)
	    cover_logo += '/cover.png'

	    # Only draw the cover if the file exists. We'll
	    # use the standard imghdr function to check if
	    # it's a real png, and not a lying one :)
	    if os.path.isfile(cover_logo) and imghdr.what(cover_logo):
                mp3info.image = cover_logo
           
	
	    # Allow per mp3 covers. As per Chris' request ;)
	    if os.path.isfile(os.path.splitext(filename)[0] + '.png'):
	    	mp3info.image = os.path.splitext(filename)[0] + '.png'

            mp3info.filename = filename
            mp3info.id3 = ID3(filename)
            if mp3info.id3.track == None:
                mp3info.id3.track = ''    # Looks better
            mp3info.drawall = 1
            skin.DrawMP3(mp3info)
            mp3info.drawall = 0

            self.thread.mode = 'play'
            self.thread.filename = filename
            self.thread.mode_flag.set()
            rc.app = self.eventhandler
        
        
    def stop(self):
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.3)


    def eventhandler(self, event):
        if event == rc.STOP or event == rc.SELECT or event == rc.MENU:
            self.stop()
            rc.app = None
            menuwidget.refresh()
	elif event == rc.PAUSE:
	    self.thread.app.write('PAUSE')
	    print "PAUSE"
        elif event == rc.FFWD:
            self.thread.app.write('JUMP +200')
        elif event == rc.REW:
            self.thread.app.write('JUMP -200')
        elif event == rc.LEFT:
            self.stop()
            # Go to the previous song in the list
            pos = self.playlist.index(self.filename)
            pos = (pos-1) % len(self.playlist)
            filename = self.playlist[pos]
            self.play(filename, self.playlist)
        elif event == rc.PLAY_END or event == rc.RIGHT:
            print 'got end of song'
            self.stop()
            pos = self.playlist.index(self.filename)
            last_file = (pos == len(self.playlist)-1)
            
            # Don't continue if at the end of the list
            if self.playlist == [] or (last_file and not self.repeat):
                self.stop()
                rc.app = None
                menuwidget.refresh()
            else:
                # Go to the next song in the list
                pos = (pos+1) % len(self.playlist)
                filename = self.playlist[pos]
                self.play(filename, self.playlist)
            

class MPG123App(childapp.ChildApp):

    def __init__(self, filename):
        # Start the app
        args = '-R ' + '"' + filename + '"'
        command = config.MPG123_APP + ' ' + args
        childapp.ChildApp.__init__(self, command)

        # Start playing the song
        self.write('LOAD ' + filename + '\n')

        
    def stdout_cb(self, str):
        if mpg123_eof(str):
            self.kill()
                    
        
class MPG123_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.mode = 'idle'
        self.mode_flag = threading.Event()
        self.filename = ''
        

    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
            elif self.mode == 'play':

                # Start the application
                self.app = MPG123App(self.filename)

                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                self.app.kill()
                
                if self.mode == 'play':
                    rc.post_event(rc.PLAY_END)
                    print 'posted end of song'
                self.mode = 'idle'
            else:
                self.mode = 'idle'

    
#
# Interpret the text output from mpg123 to determine whether it has reached the
# end of the file.
#
lastupdate = 0.0
def mpg123_eof(out):
    global lastupdate, mp3info
    
    last_line = out

    if last_line == '@P 0':
        retval = 1
    elif last_line[0:2] == '@F':
        elems = last_line.split()
        elapsed = elems[3]
        remain = elems[4]
        total = float(elapsed) + float(remain)
        done = round((float(elapsed) / total) * 100.0)
        
        if time.time() > (lastupdate + 0.5):

            lastupdate = time.time()
            el = int(round((float(elapsed))))
            rem = int(round((float(remain))))

            mp3info.elapsed = el
            mp3info.remain = rem
            mp3info.done = done
            
            skin.DrawMP3(mp3info)

        retval = 0
    else:
        retval = 0

    return retval
