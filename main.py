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
# import mp3
# No.. the music module :)
import music

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
    osd.drawstring('shutting down...', osd.width/2 - 90, osd.height/2 - 10,
                   fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
    osd.update()
    os.system("shutdown -h now")

    

def autostart():
    if config.ROM_DRIVES != None: 
        media,label,image,play_options = util.identifymedia(config.ROM_DRIVES[0][0])
        if play_options:
            movie.play(None, play_options)
        elif media == 'DIVX':
            movie.cwd(config.ROM_DRIVES[0][0], menuwidget)
        elif media == 'MP3':
            mp3.cwd(config.ROM_DRIVES[0][0], menuwidget)
        elif media == 'IMAGE':
            imenu.cwd(config.ROM_DRIVES[0][0], menuwidget)

    
#
# Setup the main menu and handle events (remote control, etc)
#
def getcmd():
    items = []

    # XXX Move icons into skin
    if config.ENABLE_TV:
        items += [menu.MenuItem('TV', tv.main_menu, 'tv', None, None, 'icons/tv.png',0)]
    items += [menu.MenuItem('MOVIES', movie.main_menu,'', None, None, 'icons/movies.png',0)]
    items += [menu.MenuItem('MUSIC', music.main_menu,'', None, None, 'icons/mp3.png',0)]
#    items += [menu.MenuItem('MUSIC', mp3.main_menu,'', None, None, 'icons/mp3.png',0)]

    items += [menu.MenuItem('IMAGES', imenu.main_menu,'',None, None, 'icons/images.png',0)]
    if config.ENABLE_SHUTDOWN:
        items += [menu.MenuItem('SHUTDOWN', shutdown, None, None, None, \
                                'icons/shutdown.png', 0) ]

    mainmenu = menu.Menu('FREEVO MAIN MENU', items, packrows=0)
    menuwidget.pushmenu(mainmenu)

    muted = 0
    mainVolume = 0
    while 1:
        
        # Get next command
        while 1:

            if 'OSD_SDL' in dir(config):  
                if '_cb' in dir(osd):
                    event = osd._cb()

                if event: break
            
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
        elif event == rc.EJECT and len(menuwidget.menustack) == 1 and config.ROM_DRIVES:
            (rom_dir, name, tray) = config.ROM_DRIVES[0]
            tray_open = tray
            config.ROM_DRIVES[0] = (rom_dir, name, (tray + 1) % 2)
            if tray_open:
                if DEBUG: print 'Inserting %s' % rom_dir

                # XXX FIXME: this doesn't look very good, we need
                # XXX some sort of a pop-up widget
                osd.drawbox(osd.width/2 - 180, osd.height/2 - 30, osd.width/2 + 180,\
                            osd.height/2+30, width=-1,
                            color=((60 << 24) | osd.COL_BLACK))
                osd.drawstring('mounting %s' % rom_dir, \
                               osd.width/2 - 160, osd.height/2 - 10,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.update()

                # close the tray and mount the cd
                os.system('eject -t %s' % rom_dir)
                os.system('mount %s' % rom_dir)
                menuwidget.refresh()
                autostart()

            else:
                if DEBUG: print 'Ejecting %s' % rom_dir
                os.system('eject %s' % rom_dir)

            
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

    # add tray status to ROM_DRIVES
    if config.ROM_DRIVES != None: 
        pos = 0
        for (dir, name) in config.ROM_DRIVES:
            config.ROM_DRIVES[pos] = (dir, name, 0)
            pos += 1

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
    os.system('killall -9 mplayer 2&> /dev/null') # ditto

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


