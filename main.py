# ----------------------------------------------------------------------
# main.py - This is the Freevo main application code
# ----------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------
# $Log$
# Revision 1.70  2002/10/01 13:46:29  dischi
# Added signal handler for SIGTERM.
# Now freevo reacts on "kill [-15] ..." for a controlled shutdown
# (osd.shutdown to restore the video modes etc.)
#
# Revision 1.69  2002/09/29 19:57:59  dischi
# Added SHUTDOWN_SYS_CMD to freevo_config to set the shutdown command
#
# Revision 1.68  2002/09/21 10:12:11  dischi
# Moved osd.popup_box to skin.PopupBox. A popup box should be part of the
# skin.
#
# Revision 1.67  2002/09/18 18:42:19  dischi
# Some small changes here and there, nothing important
#
# Revision 1.66  2002/09/15 11:53:41  dischi
# Make info in RemovableMedia a class (RemovableMediaInfo)
#
# Revision 1.65  2002/09/14 16:55:33  dischi
# cosmetic change
#
# Revision 1.64  2002/09/08 18:26:03  krister
# Applied Andrew Drummond's MAME patch. It seems to work OK on X11, but still needs some work before it is ready for prime-time...
#
# Revision 1.63  2002/09/07 06:19:44  krister
# Improved removable media support.
#
# Revision 1.62  2002/09/04 19:47:45  dischi
# wrap (u)mount to get rid of the error messages
#
# Revision 1.61  2002/09/04 19:32:31  dischi
# Added a new identifymedia. Freevo now polls the rom drives for media
# change and won't mount the drive unless you want to play a file from cd or
# you browse it.
#
# Revision 1.60  2002/09/01 09:43:01  dischi
# Fixes for the new "type" parameter in MenuItem
#
# Revision 1.59  2002/08/31 18:22:47  dischi
# changed pgrep regexp to kill freevo
#
# Revision 1.58  2002/08/31 18:09:33  krister
# Removed old code for shutting down from startup.py which is not used anymore.
#
# Revision 1.57  2002/08/21 04:58:26  krister
# Massive changes! Obsoleted all osd_server stuff. Moved vtrelease and matrox stuff to a new dir fbcon. Updated source to use only the SDL OSD which was moved to osd.py. Changed the default TV viewing app to mplayer_tv.py. Changed configure/setup_build.py/config.py/freevo_config.py to generate and use a plain-text config file called freevo.conf. Updated docs. Changed mplayer to use -vo null when playing music. Fixed a bug in music playing when the top dir was empty.
#
# Revision 1.56  2002/08/19 05:51:15  krister
# Load main menu items from the skin.
#
# Revision 1.55  2002/08/19 02:08:38  krister
# Added killall for freevo_xwin at shutdown. Fixed tabs.
#
# Revision 1.54  2002/08/17 02:57:52  krister
# Gustavi Barbieris changes for getting the main menu items from the skin.
#
# Revision 1.53  2002/08/14 12:38:05  krister
# Made shutdown loop forever until dead. This hopefully fixes a bug where SDL crashes at polling after shutdown.
#
# Revision 1.52  2002/08/14 09:28:37  tfmalt
#  o Updated all files using skin to create a skin object with the new
#    get_singleton function. Please tell or add yourself if I forgot a
#    place.
#
# Revision 1.51  2002/08/14 07:47:18  dischi
# freevo_main_quiet is now default
#
# Revision 1.50  2002/08/14 04:33:00  krister
# Bugfixes in shutdown.
#
# Revision 1.49  2002/08/14 02:40:28  krister
# Moved the runtime dir freevo_rt to ../runtime.
#
# Revision 1.48  2002/08/13 04:35:53  krister
# Removed the 1.5s delay at startup. Removed obsolete code.
#
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
import videogame      # The VideoGame Module
import mame           # The Mame Module

import identifymedia
import signal

DEBUG = 1 # Set to 1 for debug output
TRUE  = 1
FALSE = 0

mplayer = mplayer.get_singleton() # Create the mplayer object
skin    = skin.get_singleton()


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

    time.sleep(0.5)
    osd.shutdown() # SDL must be shutdown to restore video modes etc
    
    # XXX temporary kludge so it won't break on old config files
    if 'ENABLE_SHUTDOWN_SYS' in dir(config):  
        if config.ENABLE_SHUTDOWN_SYS:
            os.system(config.SHUTDOWN_SYS_CMD)
            # let freevo be killed by init, looks nicer if the picture
            # vanishes just before matroxset kills the tv out
            return

    #
    # Here are some different ways of exiting freevo for the
    # different ways that it could have been started.
    #
    
    # XXX kludge to shutdown the runtime version (no linker)
    os.system('killall -9 freevo_rt 2&> /dev/null') 
    os.system('killall -9 freevo_xwin 2&> /dev/null')  # X11 helper app
    # XXX Kludge to shutdown if started with "python main.py"
    os.system('kill -9 `pgrep -f "python.*main.py" -d" "` 2&> /dev/null') 

    # Just wait until we're dead. SDL cannot be polled here anyway.
    while 1:
        time.sleep(1)
        

#
# Eventhandler for stuff like CD inserted
#
def eventhandler(event = None, menuw=None, arg=None):
    """Automatically perform actions depending on the event, e.g. play DVD
    """

    print 'main.py:eventhandler(): event=%s, arg=%s' % (event, arg)
    menuw.refresh()
    return  # XXX autoplay is disabled for now, there's some bug...

    if event == rc.IDENTIFY_MEDIA:
        
        media = config.REMOVABLE_MEDIA[0] # XXX kludge, handle more drives
        
        if media.info:
            if media.info.play_options:
                util.mount(media.mountdir)
                movie.play_movie(menuw=None, arg=media.info.play_options)

            elif media.info.type == 'AUDIO-CD':
                print "play the audio cd -- not implemented yet"
                menuw.refresh()

            elif media.info.type == 'DIVX':
                util.mount(media.mountdir)
                movie.cwd(media.mountdir, menuwidget)

            elif media.info.type == 'AUDIO':
                util.mount(media.mountdir)
                music.parse_entry([media.mountdir, media.mountdir], menuwidget)

            elif media.info.type == 'IMAGE':
                util.mount(media.mountdir)
                imenu.cwd(media.mountdir, menuwidget)

            else:
                menuw.refresh()
        else:
            menuw.refresh()

    
#
# Setup the main menu and handle events (remote control, etc)
#
def getcmd():
    items = []

    # Load the main menu items from the skin
    menu_items = skin.settings.mainmenu.items
    for i in menu_items:
        if i.visible:
            items += [menu.MenuItem(i.name,eval(i.action), i.arg, eventhandler,
                                    None, 'main', i.icon)]
            
    mainmenu = menu.Menu('FREEVO MAIN MENU', items, packrows=0, umount_all = 1)
    menuwidget.pushmenu(mainmenu)

    muted = 0
    mainVolume = 0 # XXX We are using this for PcmVolume as well.
    while 1:
        
        # Get next command
        while 1:

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

        # Handle the EJECT key for the main menu
        elif event == rc.EJECT and len(menuwidget.menustack) == 1:

            # Are there any drives defined?
            if not config.REMOVABLE_MEDIA: continue
            
            media = config.REMOVABLE_MEDIA[0]  # The default is the first drive in the list
            media.move_tray(dir='toggle')

        # Send events to either the current app or the menu handler
        if rc.app:
            rc.app(event)
        else:
            # Menu events
            menuwidget.eventhandler(event)
        


# XXX does this belong to main.py?

class RemovableMediaInfo:

    def __init__(self, type, label = None, image = None, play_options = None, \
                 xml_file = None):
        self.type = type
        self.label = label
        self.image = image
        self.play_options = play_options
        self.xml_file = xml_file
        
    
class RemovableMedia:

    def __init__(self, mountdir='', devicename='', drivename=''):
        # This is read-only stuff for the drive itself
        self.mountdir = mountdir
        self.devicename = devicename
        self.drivename = drivename

        # Dynamic stuff
        self.tray_open = 0
        self.drive_status = None  # return code from ioctl for DRIVE_STATUS

        self.info = None
        

    def is_tray_open(self):
        return self.tray_open

    def move_tray(self, dir='toggle'):
        """Move the tray. dir can be toggle/open/close
        """

        if dir == 'toggle':
            if self.tray_open:
                dir = 'close'
            else:
                dir = 'open'

        if dir == 'open':
            if DEBUG: print 'Ejecting disc in drive %s' % self.drivename
            skin.PopupBox('Ejecting disc in drive %s' % self.drivename)
            osd.update()
            os.system('eject %s' % self.mountdir)
            self.tray_open = 1
            rc.post_event(rc.REFRESH_SCREEN)
        
        elif dir == 'close':
            if DEBUG: print 'Inserting %s' % self.drivename
            skin.PopupBox('Reading disc in drive %s' % self.drivename)
            osd.update()

            # close the tray, identifymedia does the rest,
            # including refresh screen
            os.system('eject -t %s' % self.mountdir)
            self.tray_open = 0
    
    def mount(self):
        """Mount the media
        """

        if DEBUG: print 'Mounting disc in drive %s' % self.drivename
        skin.PopupBox('Locking disc in drive %s' % self.drivename)
        osd.update()
        util.mount(self.mountdir)
        return

    
    def umount(self):
        """Mount the media
        """

        if DEBUG: print 'Unmounting disc in drive %s' % self.drivename
        skin.PopupBox('Releasing disc in drive %s' % self.drivename)
        osd.update()
        util.umount(self.mountdir)
        return
    

def signal_handler(sig, frame):
    if sig == signal.SIGTERM:
        osd.clearscreen(color=osd.COL_BLACK)
        osd.shutdown() # SDL must be shutdown to restore video modes etc

        # XXX kludge to shutdown the runtime version (no linker)
        os.system('killall -9 freevo_rt 2&> /dev/null') 
        os.system('killall -9 freevo_xwin 2&> /dev/null')  # X11 helper app
        # XXX Kludge to shutdown if started with "python main.py"
        os.system('kill -9 `pgrep -f "python.*main.py" -d" "` 2&> /dev/null') 

    
#
# Main init
#
def main_func():

    # Add the drives to the config.removable_media list. There doesn't have
    # to be any drives defined.
    if config.ROM_DRIVES != None: 
        for i in range(len(config.ROM_DRIVES)):
            (dir, device, name) = config.ROM_DRIVES[i]
            media = RemovableMedia(mountdir=dir, devicename=device,
                                   drivename=name)
            media.move_tray(dir='close')
            osd.clearscreen(color=osd.COL_BLACK)
            osd.update()
            config.REMOVABLE_MEDIA.append(media)

    # Remove the ROM_DRIVES member to make sure it is not used by
    # legacy code!
    del config.ROM_DRIVES
    
    # Make sure there's no mplayer process lying around.
    os.system('killall -9 mplayer 2&> /dev/null') # XXX This is hardcoded, because
                                                  # my mplayer command is actually
                                                  # nice --10 mplayer, to run mplayer
                                                  # with higher priority, but won't be
                                                  # killed by this. 
                                                  # If I'm the only one, add this:
                                                  # ...-9 %s... ' % config.MPLAYER_CMD)

    signal.signal(signal.SIGTERM, signal_handler)

    # Start identifymedia thread
    im = identifymedia.Identify_Thread()
    im.start()
    
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
