#
# mp3.py
#
# This is the Freevo MP3 module. 
#

import sys
import random
import time, os, glob
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


# Module variable that contains an initialized MPG123() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MPG123()
        
    return _singleton


class MPG123:

    def __init__(self):
        self.thread = MPG123_Thread()
        self.thread.start()


    def play(self, filename, playlist):
        self.filename = filename
        self.playlist = playlist
        
        if not os.path.isfile(filename):
            osd.clearscreen()
            osd.drawstring('xxx', 'File "%s" not found!' % filename, 30, 280)
            time.sleep(2.0)
            menuwidget.refresh()
        else:
            osd.clearscreen()
            osd.drawstring('xxx', 'mpg123 "%s"' % filename, 30, 490)
            self.thread.mode = 'play'
            self.thread.filename = filename
            self.thread.mode_flag.set()
            rc.app = self.eventhandler

            id = ID3(filename)

            osd.drawstring('xxx', 'Title: %s' % id.title, 30, 80)
            osd.drawstring('xxx', 'Artist: %s' % id.artist, 30, 110)
            osd.drawstring('xxx', 'Album: %s' % id.album, 30, 140)
            osd.drawstring('xxx', 'Year: %s' % id.year, 30, 170)
        
        
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
        elif event == rc.FFWD:
            self.thread.app.write('JUMP +100')
        elif event == rc.REW:
            self.thread.app.write('JUMP -100')
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
            # Go to the next song in the list
            pos = self.playlist.index(self.filename)
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
old_done = 0
def mpg123_eof(out):
    last_line = out

    #print 'Got last line (%d, %d) = "%s"' % (eol1, eol2, last_line)

    if last_line == '@P 0':
        retval = 1
    elif last_line[0:2] == '@F':
        elems = last_line.split()
        elapsed = elems[3]
        remain = elems[4]
        total = float(elapsed) + float(remain)
        done = int(round((float(elapsed) / total) * 1000))
        global old_done
        if done != old_done:
            old_done = done
            el = int(round((float(elapsed))))
            rem = int(round((float(remain))))
            osd.drawstring('xxx', 'Elapsed: %s   ' % el, 30, 250)
            osd.drawstring('xxx', 'Remain: %s   ' % rem, 30, 290)
            osd.drawstring('xxx', 'Done: %5.1f%%   ' % (done / 10.0), 30, 330)
            osd.drawbox(33, 370, 635, 390, width = 3)
            osd.drawbox(43, 380, 625, 380, width = 9, color = osd.default_bg_color)
            pixels = int(round((done / 10.0) * 6.0))
            for i in range(19):
                y = 371 + i
                osd.drawline(34, y, 34 + pixels, y, color = 0x038D11)
        retval = 0
    else:
        retval = 0

    return retval
