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

    __muted    = 0
    __igainvol = 0
    
    def __init__(self):
        self.thread = V4L1TV_Thread()
        self.thread.start()
        self.tuner_chidx = 0    # Current channel, index into config.TV_CHANNELS
        

    def TunerSetChannel(self, tuner_channel):
        for pos in range(len(config.TV_CHANNELS)):
            channel = config.TV_CHANNELS[pos]
            if channel[2] == tuner_channel:
                self.tuner_chidx = pos
                return
        print 'ERROR: Cannot find tuner channel "%s" in the TV channel listing' % tuner_channel
        self.tuner_chidx = 0


    def TunerGetChannel(self):
        return config.TV_CHANNELS[self.tuner_chidx][2]


    def TunerNextChannel(self):
        self.tuner_chidx = (self.tuner_chidx+1) % len(config.TV_CHANNELS)


    def TunerPrevChannel(self):
        self.tuner_chidx = (self.tuner_chidx-1) % len(config.TV_CHANNELS)

        
    def Play(self, mode, tuner_channel=None):

        if tuner_channel != None:
            
            try:
                self.TunerSetChannel(tuner_channel)
            except ValueError:
                pass
            
        if mode == 'tv':
            tuner_channel = self.TunerGetChannel()
            inital_channel = '"' + config.TV_SETTINGS + ' ' + tuner_channel + '"'
            command = config.WATCH_TV_APP + ' ' + inital_channel
        elif mode == 'vcr':
            command = config.WATCH_TV_APP + ' "' + config.VCR_SETTINGS + ' 2"'  # Channel isn't used
        else:
            now = time.localtime(time.time())
            outfile = time.strftime("0_rec_%Y-%m-%d_%H%M%S.avi", now)
            outfile = config.DIR_RECORD + '/' + outfile
            command = (config.VIDREC_MQ % outfile)

        self.mode = mode

        # XXX Mixer manipulation code.
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setPcmVolume( 0 )
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setMainVolume( 0 )
        if config.CONTROL_ALL_AUDIO:
            mixer.setLineinVolume( 0 )
            mixer.setIgainVolume( 0 )
            mixer.setMicVolume( 0 )

        # XXX Should be moved out in appropriate functions.
        osd.clearscreen(color=osd.COL_BLACK)
        osd.drawstring('Running the "%s" application' % mode, 30, 280,
                       fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
        self.thread.mode = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        
        rc.app = self.EventHandler

        # Suppress annoying audio clicks
        time.sleep(0.5)
        # XXX Hm.. This is hardcoded and very unflexible.
        if mode == 'vcr':
            mixer.setMicVolume( config.VCR_IN_VOLUME )
        else:
            mixer.setLineinVolume( config.TV_IN_VOLUME )
            mixer.setIgainVolume( config.TV_IN_VOLUME )
            
        print 'started %s app' % self.mode
        
        
    def Stop(self):
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setPcmVolume( config.MAX_VOLUME )
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setMainVolume( config.MAX_VOLUME )
        mixer.setLineinVolume( 0 )
        mixer.setMicVolume( 0 )
        mixer.setIgainVolume( 0 ) # Input on emu10k cards.

        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.3)
        print 'stopped %s app' % self.mode


    def channel_change_do_stuff( self ):
        """This is a helper function for channel up and down events"""
        linein_vol = mixer.getLineinVolume()
        igain_vol  = mixer.getIgainVolume()
        
        mixer.setLineinVolume( 0 )
        mixer.setIgainVolume( 0 ) # Input from TV om emu10k1 cards.

        tuner_channel = self.TunerGetChannel()
        self.thread.app.write( config.TV_SETTINGS + ' ' +
                               tuner_channel + '\n' )
        time.sleep(0.1)
        mixer.setLineinVolume( linein_vol )
        mixer.setIgainVolume( igain_vol )
        

    def EventHandler(self, event):
        print '%s app got %s event' % (self.mode, event)
        if event == rc.MENU or event == rc.STOP or event == rc.SELECT or event == rc.PLAY_END:
            self.Stop()
            rc.app = None
            menuwidget.refresh()
        elif event == rc.CHUP:
            if self.mode == 'vcr':
                return
            # Go to the next channel in the list
            self.TunerNextChannel()
            self.channel_change_do_stuff()
            
        elif event == rc.CHDOWN:
            if self.mode == 'vcr':
                return
            # Go to the previous channel in the list
            self.TunerPrevChannel()
            self.channel_change_do_stuff()
            
        elif event == rc.LEFT:
            if self.mode == 'vcr':
                return
            # Finetune minus
            mixer.setLineinVolume( 0 )
            mixer.setIgainVolume( 0 )
            self.thread.app.write( config.TV_SETTINGS + ' ' +
                                   'fine_minus' + '\n' )
            time.sleep(0.1)
            mixer.setLineinVolume( config.TV_IN_VOLUME )
            mixer.setIgainVolume( config.TV_IN_VOLUME )
            
        elif event == rc.RIGHT:
            if self.mode == 'vcr':
                return
            # Finetune minus
            mixer.setLineinVolume( 0 )
            mixer.setIgainVolume( 0 )
            self.thread.app.write( config.TV_SETTINGS + ' ' +
                                   'fine_plus' + '\n' )
            time.sleep(0.1)
            mixer.setLineinVolume( config.TV_IN_VOLUME )
            mixer.setIgainVolume( config.TV_IN_VOLUME )

        elif event == rc.VOLUP:
            mixer.incIgainVolume()

        elif event == rc.VOLDOWN:
            mixer.decIgainVolume()

        elif event == rc.MUTE:
            if self.__muted:
                mixer.setIgainVolume( self.__igainvol )
                self.__muted = 0
            else:
                self.__igainvol = mixer.getIgainVolume()
                mixer.setIgainVolume( 0 )
                self.__muted = 1
                
                
            

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


