# ----------------------------------------------------------------------
# main.py - This is the Freevo main application code
# ----------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------
# $Log$
# Revision 1.47  2002/08/13 01:21:42  krister
# Hide output from the shutdown commands.
#
# Revision 1.46  2002/08/12 11:36:33  dischi
# removed some unneeded code
#
# Revision 1.45  2002/08/11 19:23:35  krister
# Updated shutdown code.
#
# Revision 1.44  2002/08/11 17:03:50  krister
# Removed delay after crash. Updated the shutdown process.
#
# Revision 1.43  2002/08/11 09:05:18  krister
# Added a killall for the runtime tasks at shutdown.
#
# Revision 1.42  2002/08/08 06:05:32  outlyer
# Small changes:
#  o Made Images menu a config file option "ENABLE_IMAGES"
#  o Removed the redundant fbset 640x480-60 which doesn't even exist in the
#    fbset.db (?)
#
# Revision 1.41  2002/08/07 04:53:01  krister
# Changed shutdown to just exit freevo. A new config variable can be set to shutdown the entire machine.
#
# Revision 1.40  2002/08/05 00:45:50  tfmalt
# o Started work in a popup widget / dialog box type thing.
#   Changed the "mouting /mnt/cdrom" entry on EJECT and put it in osd.py
#
# Revision 1.39  2002/08/04 22:17:44  tfmalt
# o Fixed autostart so that it handles CD's of type AUDIO properly again.
#
# ----------------------------------------------------------------------
#
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
# -----------------------------------------------------------------------

import config
import sys, socket, random, time, os
import traceback

import util    # Various utilities
import menu    # The menu widget class
import skin    # The skin class
import mixer   # The mixer class
import osd     # The OSD class, used to communicate with the OSD daemon
import rc      # The RemoteControl class.
import music   # The Music module
import movie   # The Movie module
import tv      # The TV module
import imenu   # The Image viewer module
import mplayer


DEBUG = 1 # Set to 1 for debug output
TRUE  = 1
FALSE = 0


# Create the mplayer object
mplayer = mplayer.get_singleton()

###############################################################################

# Set up the mixer
# XXX Doing stuff to select correct device to manipulate.
mixer = mixer.get_singleton()

if config.MAJOR_AUDIO_CTRL == 'VOL':
    mixer.setMainVolume( config.DEFAULT_VOLUME )
    if config.CONTROL_ALL_AUDIO:
        mixer.setPcmVolume( config.MAX_VOLUME )
        # XXX This is for SB Live cards should do nothing to others
        # XXX Please tell if you have problems with this.
        mixer.setOgainVolume( config.MAX_VOLUME )
elif config.MAJOR_AUDIO_CTRL == 'PCM':
    mixer.setPcmVolume( config.DEFAULT_VOLUME )
    if config.CONTROL_ALL_AUDIO:
        mixer.setMainVolume( config.MAX_VOLUME )
        # XXX This is for SB Live cards should do nothing to others
        # XXX Please tell if you have problems with this.
        mixer.setOgainVolume( config.MAX_VOLUME )
else:
    if DEBUG: print "No appropriate audio channel found for mixer"

if config.CONTROL_ALL_AUDIO:
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

    # XXX temporary kludge so it won't break on old config files
    if 'ENABLE_SHUTDOWN_SYS' in dir(config):  
        if config.ENABLE_SHUTDOWN_SYS:
            os.system("shutdown -h now")

    #
    # Here are some different ways of exiting freevo for the
    # different ways that it could have been started.
    #
    
    # XXX kludge to signal startup.py to abort
    os.system('touch /tmp/freevo-shutdown') 
    # XXX kludge to shutdown the runtime version (linker)
    os.system('killall -9 freevo_rt/ld-linux.so.2 2&> /dev/null') 
    # XXX kludge to shutdown the runtime version (no linker)
    os.system('killall -9 freevo_rt/freevo_rt 2&> /dev/null') 
    # XXX Kludge to shutdown if started with "python main.py"
    os.system('kill -9 `pgrep -f "python main.py" -d" "` 2&> /dev/null') 


def autostart():
    if config.ROM_DRIVES != None: 
        media,label,image,play_options = util.identifymedia(config.ROM_DRIVES[0][0])
        if play_options:
            movie.play_movie(None, play_options)
        elif media == 'DIVX':
            movie.cwd(config.ROM_DRIVES[0][0], menuwidget)
        elif media == 'AUDIO':
            music.parse_entry([config.ROM_DRIVES[0][0],
                               config.ROM_DRIVES[0][0]],
                              menuwidget)
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
    if config.ENABLE_IMAGES:
        items += [menu.MenuItem('IMAGES', imenu.main_menu,'',None, None, 'icons/images.png',0)]
    if config.ENABLE_SHUTDOWN:
        items += [menu.MenuItem('SHUTDOWN', shutdown, None, None, None, \
                                'icons/shutdown.png', 0) ]

    mainmenu = menu.Menu('FREEVO MAIN MENU', items, packrows=0)
    menuwidget.pushmenu(mainmenu)

    muted = 0
    mainVolume = 0 # XXX We are using this for PcmVolume as well.
    while 1:
        
        # Get next command
        while 1:

            if 'OSD_SDL' in dir(config):  
                event = osd._cb()
                if event: break
            
            event = rc.poll()
            if event == rc.NONE:
                time.sleep(0.1) # give a little time for buffers to fill
            else:
                break

        # Handle volume control   XXX move to the skin
        if event == rc.VOLUP:
            print "Got VOLUP in main!"
            if( config.MAJOR_AUDIO_CTRL == 'VOL' ):
                mixer.incMainVolume()
            elif( config.MAJOR_AUDIO_CTRL == 'PCM' ):
                mixer.incPcmVolume()
                
        elif event == rc.VOLDOWN:
            if( config.MAJOR_AUDIO_CTRL == 'VOL' ):
                mixer.decMainVolume()
            elif( config.MAJOR_AUDIO_CTRL == 'PCM' ):
                mixer.decPcmVolume()
                
        elif event == rc.MUTE:
            if muted:
                if config.MAJOR_AUDIO_CTRL == 'VOL':
                    mixer.setMainVolume( mainVolume )
                elif config.MAJOR_AUDIO_CTRL == 'PCM':
                    mixer.setPcmVolume( mainVolume )
                muted = 0
            else:
                if config.MAJOR_AUDIO_CTRL == 'VOL':
                    mainVolume = mixer.getMainVolume()
                    mixer.setMainVolume(0)
                elif config.MAJOR_AUDIO_CTRL == 'PCM':
                    mainVolume = mixer.getPcmVolume()
                    mixer.setPcmVolume(0)
                muted = 1
        elif event == rc.EJECT and len(menuwidget.menustack) == 1 and config.ROM_DRIVES:
            (rom_dir, name, tray) = config.ROM_DRIVES[0]
            tray_open = tray
            config.ROM_DRIVES[0] = (rom_dir, name, (tray + 1) % 2)
            if tray_open:
                if DEBUG: print 'Inserting %s' % rom_dir
                osd.popup_box( 'mounting %s' % rom_dir )
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

    # Make sure there's no mplayer process lying around.
    os.system('killall -9 mplayer 2&> /dev/null') # XXX This is hardcoded, because
    						  # my mplayer command is actually
						  # nice --10 mplayer, to run mplayer
						  # with higher priority, but won't be
						  # killed by this. 
						  # If I'm the only one, add this:
						  # ...-9 %s... ' % config.MPLAYER_CMD)

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


