#if 0
# -----------------------------------------------------------------------
# mame.py - the Freevo mame module. 
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
skin       = skin.get_singleton()

# Module variable that contains an initialized Mame() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Mame()
        
    return _singleton

class Mame:

    def __init__(self):
        self.thread = Mame_Thread()
        self.thread.start()
        self.mode = None
                         
    def play(self, mode, filename, playlist, repeat=0, mame_options=""):

        if DEBUG:
            print 'mame.play(): mode=%s, filename=%s' % (mode, filename)
            
        self.mode   = mode   # setting global var to mode.
        self.repeat = repeat # Repeat playlist setting

        if( (mode == 'mame') and
            not os.path.isfile(filename) ):
            osd.clearscreen()
            osd.drawstring('File "%s" not found!' % filename, 30, 280)
            osd.update()
            time.sleep(2.0) 
            menuwidget.refresh()
            return 0
       
        # build mame command

        mpl = '--prio=%s %s %s' % (config.MAME_NICE,
                                        config.MAME_CMD,
                                        config.MAME_ARGS_DEF)

        if mode == 'mame':

            # Add special arguments for the whole playlist from the
            # XML file
            if mame_options:
                mpl += (' ' + mame_options)
                if DEBUG: print 'options, mpl = "%s"' % mpl

            # Some files needs special arguments to mame, they can be
            # put in a <filename>.mame options file. The <filename>
            # includes the suffix (.avi, etc)!
            # The arguments in the options file are added at the end of the
            # regular mame arguments.
            if os.path.isfile(filename + '.mame'):
                mpl += (' ' + open(filename + '.mame').read().strip())
                if DEBUG: print 'Read options, mpl = "%s"' % mpl


            romname = os.path.basename(filename)
            romdir = os.path.dirname(filename)
            command = '%s -rp %s "%s"' % (mpl, romdir, romname)

        self.filename = filename 
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
                
        mixer.setIgainVolume( 0 ) # SB Live input from TV Card.
        # This should _really_ be set to zero when playing other audio.

        # clear the screen for mame
        osd.clearscreen(color=osd.COL_BLACK)
        osd.update()

        self.mame_options = mame_options

        if DEBUG:
            print 'Mame.play(): Starting thread, cmd=%s' % command
            
        self.thread.mode    = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        rc.app = self.eventhandler
        
    def stop(self):
        # self.thread.audioinfo = None
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.3)


    def eventhandler(self, event):
        if event == rc.STOP or event == rc.SELECT:
            self.stop()
            rc.app = None
            menuwidget.refresh()
        elif event == rc.MENU:
            self.thread.app.write('M')
        elif event == rc.DISPLAY:
            self.thread.cmd( 'config' )
        elif event == rc.PAUSE or event == rc.PLAY:
            self.thread.cmd('pause')
        elif event == rc.ENTER:
            self.thread.cmd('reset')
        elif event == rc.REC:
            self.thread.cmd('snapshot')
            
# ======================================================================
class MameApp(childapp.ChildApp):
        
    def kill(self):
        childapp.ChildApp.kill(self, signal.SIGINT)
        osd.update()


# ======================================================================
class Mame_Thread(threading.Thread):

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
                    print 'Mame_Thread.run(): Started, cmd=%s' % self.command
                
                osd.stopdisplay()     
                self.app = MameApp(self.command)
                time.sleep(2.0)
                osd.restartdisplay()
                #time.sleep(1.0)
                #os.system('./fbcon/mga_ntsc_768x576.sh')

                while self.mode == 'play' and self.app.isAlive():
                    # if DEBUG: print "Still running..."
                    time.sleep(0.1)

                self.app.kill()

                if self.mode == 'play':
                    rc.post_event(rc.STOP)

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'


    def cmd(self, command):
        print "In cmd going to do: " + command
        str = ''
        if command == 'config':
            str = mameKey('CONFIGMENU')
        elif command == 'pause':
            str = mameKey('PAUSE')
        elif command == 'reset':
            str = mameKey('RESET')
        elif command == 'exit':
            str = mameKey('EXIT')
        elif command == 'snapshot':
            str = mameKey('SNAPSHOT')

        self.app.write(str) 


#
# Translate an abstract remote control command to an mame
# command key
#
def mameKey(rcCommand):
    mameKeys = {
        'CONFIGMENU'     : '\x09',
        'PAUSE'          : 'P',
        'RESET'          : '\x1b[[13~',
        'EXIT'           : '\x1b',
        'SNAPSHOT'       : '\x1b[[24~'
        }
    
    key = mameKeys.get(rcCommand, '')

    return key


# Test code
if __name__ == '__main__':
    player = get_singleton()

    player.play('audio', sys.argv[1], None)
