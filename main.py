#
# main.py
#
# This is the Freevo main application code.
#
# $Id$

# Configuration file. Determines where to look for AVI/MP3 files, etc
# Logging is initialized here, so it should be imported first
import config

import sys, socket, random, time, os
import traceback

# Various utilities
import util

# The menu widget class
import menu

# The skin class
import skin

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

# The Image viewer module
import imenu

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

import mplayer

# Create the mplayer object
mplayer = mplayer.get_singleton()

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

def shutdown(menuw=None, arg=None):
    osd.clearscreen(color=osd.COL_BLACK)
    osd.drawstring('shutting down', osd.width/2 - 90, osd.height/2 - 10,
                   fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
    osd.update()
    os.system("sutdown -h now")

    

def autostart():
    if os.path.exists(config.CD_MOUNT_POINT + "/mpegav/"):
        if DEBUG: print 'Autstart VCD'
        mplayer.play('vcd', '1', [])
    elif os.path.exists(config.CD_MOUNT_POINT + "/video_ts/"):
        if DEBUG: print 'Autstart DVD'
        mplayer.play('dvd', '1', [])
    else:
        mplayer_files = util.match_files(config.CD_MOUNT_POINT, \
                                         config.SUFFIX_MPLAYER_FILES)
        mp3_files = util.match_files(config.CD_MOUNT_POINT, \
                                     config.SUFFIX_MPG123_FILES)
        image_files = util.match_files(config.CD_MOUNT_POINT, \
                                       config.SUFFIX_IMAGE_FILES)
        if mplayer_files and not mp3_files and not image_files:
            if DEBUG: print 'Autstart movie cd'
            movie.cwd(config.CD_MOUNT_POINT, menuwidget)
        elif not mplayer_files and mp3_files and not image_files:
            if DEBUG: print 'Autstart mp3 cd'
            mp3.cwd(config.CD_MOUNT_POINT, menuwidget)
        elif not mplayer_files and not mp3_files and image_files:
            if DEBUG: print 'Autstart image cd'
            imenu.cwd(config.CD_MOUNT_POINT, menuwidget)

    
#
# Setup the main menu and handle events (remote control, etc)
#
def getcmd():
    items = []
    items += [menu.MenuItem('TV', tv.main_menu, 'tv','icons/tv.png',0)]  # XXX Move icons into skin
    items += [menu.MenuItem('MOVIES', movie.main_menu,'','icons/movies.png',0)]
    items += [menu.MenuItem('MUSIC', mp3.main_menu,'','icons/mp3.png',0)]
    items += [menu.MenuItem('DVD/CD', movie.play_movie, ('dvd', '1', []),'icons/dvd.png',0)]  # XXX Add DVD title handling
    items += [menu.MenuItem('VCD', movie.play_movie, ('vcd', '1', []))]
    #items += [menu.MenuItem('RECORD MOVIE', tv.main_menu, 'record')]

    items += [menu.MenuItem('IMAGES', imenu.main_menu,'','icons/images.png',0)]
    items += [menu.MenuItem('SHUTDOWN', shutdown, None) ]

    mainmenu = menu.Menu('FREEVO MAIN MENU', items, packrows=0)
    menuwidget.pushmenu(mainmenu)
    
    muted = 0
    mainVolume = 0
    tray_open = 1
    while 1:
        
        # Get next command
        while 1:
            event = rc.poll()
            if event == rc.NONE:
                time.sleep(0.1) # give a little time for buffers to fill
            else:
                break

        # Handle volume control   XXX move to the skin
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
        elif event == rc.EJECT:
            if tray_open:
                if DEBUG: print 'Inserting %s' % config.CD_MOUNT_POINT

                # XXX FIXME: this doesn't look very good, we need
                # XXX some sort of a pop-up widget
                osd.drawbox(osd.width/2 - 180, osd.height/2 - 30, osd.width/2 + 180,\
                            osd.height/2+30, width=-1,
                            color=((60 << 24) | osd.COL_BLACK))
                osd.drawstring('mounting %s' % config.CD_MOUNT_POINT, \
                               osd.width/2 - 160, osd.height/2 - 10,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.update()

                # close the tray and mount the cd
                os.system('eject -t %s' % config.CD_MOUNT_POINT)
                os.system('mount %s' % config.CD_MOUNT_POINT)
                menuwidget.refresh()
                tray_open = 0
                if len(menuwidget.menustack) == 1:
                    autostart()

            else:
                if DEBUG: print 'Ejecting %s' % config.CD_MOUNT_POINT
                os.system('eject %s' % config.CD_MOUNT_POINT)
                tray_open = 1

            
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
    
    # Make sure there's no mpg123 process lying around.
    # XXX change, we don't want to kill any mpg123 that is not started by Freevo :-)
    os.system('killall -9 mpg123 2&> /dev/null') # XXX hardcoded, fix!

    time.sleep(1.5)
    
    # Kick off the main menu loop
    print 'Main loop starting...'
    getcmd()


#
# Main function
#
if __name__ == "__main__":
    try:
        main_func()
    except:
        print 'Crash!'
        traceback.print_exc()
        time.sleep(5)


