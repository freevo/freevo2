#
# v4l1tv.py
#
# This is the Freevo v4l1tv module.
#
# $Id$

import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading
import signal


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


# Module variable that contains an initialized V4L1TV() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = V4L1TV()
        
    return _singleton


class V4L1TV:

    def __init__(self):
        self.thread = V4L1TV_Thread()
        self.thread.start()
        self.channel_pos = 0
        

    def play(self, mode, channel=None):

        if channel != None:
            try:
                self.channel_pos = config.TV_CHANNELS.index(channel)
            except ValueError:
                pass
            
        if mode == 'tv':
            channel_name = config.TV_CHANNELS[self.channel_pos]
            inital_channel = '"' + config.TV_SETTINGS + ' ' + channel_name + '"'
            command = config.WATCH_TV_APP + ' ' + inital_channel
        elif mode == 'vcr':
            command = config.WATCH_TV_APP + ' "' + config.VCR_SETTINGS + ' 2"'  # Channel isn't used
        else:
            now = time.localtime(time.time())
            outfile = time.strftime("0_rec_%Y-%m-%d_%H%M%S.avi", now)
            outfile = config.DIR_RECORD + '/' + outfile
            command = (config.VIDREC_MQ % outfile)

        self.mode = mode
        
        mixer.setPcmVolume(0)
        mixer.setLineinVolume(0)
        mixer.setMicVolume(0)

        osd.clearscreen(color=osd.COL_BLACK)
        osd.drawstring('xxx', 'Running the "%s" application' % mode, 30, 280,
                       fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
        self.thread.mode = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        
        rc.app = self.eventhandler

        # Suppress annoying audio clicks
        time.sleep(0.5)
        if mode == 'vcr':
            mixer.setMicVolume(90)
        else:
            mixer.setLineinVolume(90)
        print 'started %s app' % self.mode
        
        
    def stop(self):
        mixer.setPcmVolume(100)
        mixer.setLineinVolume(0)
        mixer.setMicVolume(0)

        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.3)
        print 'stopped %s app' % self.mode


    def eventhandler(self, event):
        print '%s app got %s event' % (self.mode, event)
        if event == rc.MENU or event == rc.STOP or event == rc.SELECT or event == rc.PLAY_END:
            self.stop()
            rc.app = None
            menuwidget.refresh()
        elif event == rc.CHUP:
            if self.mode == 'vcr':
                return
            # Go to the next channel in the list
            self.channel_pos = (self.channel_pos+1) % len(config.TV_CHANNELS)
            channel = config.TV_CHANNELS[self.channel_pos]
            mixer.setLineinVolume(0)
            self.thread.app.write(config.TV_SETTINGS + ' ' + channel + '\n')
            time.sleep(0.1)
            mixer.setLineinVolume(90)
        elif event == rc.CHDOWN:
            if self.mode == 'vcr':
                return
            # Go to the previous channel in the list
            self.channel_pos = (self.channel_pos-1) % len(config.TV_CHANNELS)
            channel = config.TV_CHANNELS[self.channel_pos]
            mixer.setLineinVolume(0)
            self.thread.app.write(config.TV_SETTINGS + ' ' + channel + '\n')
            time.sleep(0.1)
            mixer.setLineinVolume(90)
        elif event == rc.LEFT:
            if self.mode == 'vcr':
                return
            # Fintune minus
            mixer.setLineinVolume(0)
            self.thread.app.write(config.TV_SETTINGS + ' ' + 'fine_minus' + '\n')
            time.sleep(0.1)
            mixer.setLineinVolume(90)
        elif event == rc.RIGHT:
            if self.mode == 'vcr':
                return
            # Fintune minus
            mixer.setLineinVolume(0)
            self.thread.app.write(config.TV_SETTINGS + ' ' + 'fine_plus' + '\n')
            time.sleep(0.1)
            mixer.setLineinVolume(90)
            


class V4L1TV_Thread(threading.Thread):

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

                print 'thread, starting cmd = "%s"' % self.command
                
                self.app = childapp.ChildApp(self.command)
                
                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                print 'thread done, alive = %s' % self.app.isAlive()
                
                # Use SIGINT (=CTRL-C) so that NVrec stops properly
                self.app.kill(signal.SIGINT)
                
                while self.app.isAlive():
                    time.sleep(0.1)

                if self.mode == 'play':
                    rc.post_event(rc.PLAY_END)
                self.mode = 'idle'
            else:
                self.mode = 'idle'


