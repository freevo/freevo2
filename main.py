#
# main.py
#
# This is the Freevo main application code.
#

import sys, socket, random, time, os
import traceback

if 0:
    # Redirect stdout and stderr to log files, timestamp them
    sys.stderr = open('./log_main_err', 'a', 0)
    sys.stderr.write('\n\n' + time.ctime(time.time()) + '\n')

    sys.stdout = open('./log_main_out', 'a', 0)
    sys.stdout.write('\n\n' + time.ctime(time.time()) + '\n')

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The menu widget class
import menu

# The mixer class, controls the volumes for playback and recording
import mixer

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# The MP3 module
import mp3

# The Movie module
import movie

# The TV module
import tv

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

###############################################################################

# Set up the mixer
mixer = mixer.get_singleton()
mixer.setMainVolume(40)
mixer.setPcmVolume(100)
mixer.setLineinVolume(0)
mixer.setMicVolume(0)

# Create the remote control object
rc = rc.get_singleton()

# Create the OSD object
osd = osd.get_singleton()

# Create the MenuWidget object
menuwidget = menu.get_singleton()


#
# Setup the main menu and handle events (remote control, etc)
#
def getcmd():
    items = []
    items += [menu.MenuItem('TV', tv.main_menu, 'tv')]
    items += [menu.MenuItem('MOVIES', movie.main_menu)]
    items += [menu.MenuItem('MUSIC', mp3.main_menu)]
    items += [menu.MenuItem('DVD/CD', movie.play_movie, ('dvd', '1', []))]  # XXX Add DVD title handling
    items += [menu.MenuItem('RECORD MOVIE', tv.main_menu, 'record')]

    mainmenu = menu.Menu('FREEVO MAIN MENU', items, packrows=0)
    
    menuwidget.pushmenu(mainmenu)
    
    muted = 0
    mainVolume = 0
    while 1:
        
        # Get next command
        while 1:
            event = rc.poll()
            if event == rc.NONE:
                time.sleep(0.1) # give a little time for buffers to fill
            else:
                break

        # Handle volume control
        if event == rc.VOLUP:
            mixer.incMainVolume()
        elif event == rc.VOLDOWN:
            mixer.decMainVolume()
        elif event == rc.MUTE:
            if muted:
                mixer.setMainVolume(mainVolume)
                muted = 0
            else:
                mainVolume = mixer.getMainVolume()
                mixer.setMainVolume(0)
                muted = 1

        # Send events to either the current app or the menu handler
        if rc.app:
            rc.app(event)
        else:
            # Menu events
            menuwidget.eventhandler(event)
        
    
#
# Main init
#
def main_func():

    # Parse the command-line arguments
    video = 'sim'
    for arg in sys.argv[1:]:
        if arg == '--videotools=real':
            video = 'real'

    # Run-time configuration settings
    config.ConfigInit(videotools = video)
    
    # Turn off the MGA back-end scaler, it will clobber the framebuffer otherwise
    os.system('./matrox_g400/mga_bes_off 2&> /dev/null') # XXX hardcoded, fix!

    # Make sure there's no mpg123 process lying around.
    # XXX change, we don't want to kill any mpg123 that is not started by Freevo :-)
    os.system('killall -9 mpg123 2&> /dev/null') # XXX hardcoded, fix!

   # Kick off the main menu loop
    print 'Main loop starting...'
    getcmd()


#
# Main function
#
if __name__ == "__main__":
    print os.getcwd()
    try:
        main_func()
    except:
        print 'Crash!'
        traceback.print_exc()
        time.sleep(5)


