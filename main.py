# ----------------------------------------------------------------------
# main.py - This is the Freevo main application code
# ----------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------
# $Log$
# Revision 1.76  2002/10/21 02:31:38  krister
# Set DEBUG = config.DEBUG.
#
# Revision 1.75  2002/10/16 02:48:49  krister
# Cosmetic changes.
#
# Revision 1.74  2002/10/13 14:08:31  dischi
# Don't show crash screen on keyboard interrupt
# Don't show "reading cdrom info" popup at startup
#
# Revision 1.73  2002/10/09 03:03:03  krister
# Updated for new runtime (freevo_rt -> freevo_python). Added debug info at crash.
#
# Revision 1.72  2002/10/06 14:58:51  dischi
# Lots of changes:
# o removed some old cvs log messages
# o some classes without member functions are in datatypes.py
# o movie_xml.parse now returns an object of MovieInformation instead of
#   a long list
# o mplayer_options now works better for options on cd/dvd/vcd
# o you can disable -wid usage
# o mplayer can play movies as strings or as FileInformation objects with
#   mplayer_options
#
# Revision 1.71  2002/10/05 18:10:56  dischi
# Added support for a local_skin.xml file. See Docs/documentation.html
# section 4.1 for details. An example is also included.
#
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
import osd     # The OSD class, used to communicate with the OSD daemon
import menu    # The menu widget class
import skin    # The skin class
import mixer   # The mixer class
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

# Some datatypes we need
from datatypes import *

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

mplayer = mplayer.get_singleton() # Create the mplayer object
skin    = skin.get_singleton()


# Set up the mixer
# XXX Doing stuff to select correct device to manipulate.
mixer = mixer.get_singleton()

if config.MAJOR_AUDIO_CTRL == 'VOL':
    mixer.setMainVolume(config.DEFAULT_VOLUME)
    if config.CONTROL_ALL_AUDIO:
        mixer.setPcmVolume(config.MAX_VOLUME)
        # XXX This is for SB Live cards should do nothing to others
        # XXX Please tell if you have problems with this.
        mixer.setOgainVolume(config.MAX_VOLUME)
elif config.MAJOR_AUDIO_CTRL == 'PCM':
    mixer.setPcmVolume(config.DEFAULT_VOLUME)
    if config.CONTROL_ALL_AUDIO:
        mixer.setMainVolume(config.MAX_VOLUME)
        # XXX This is for SB Live cards should do nothing to others
        # XXX Please tell if you have problems with this.
        mixer.setOgainVolume(config.MAX_VOLUME)
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

def shutdown(menuw=None, arg=None, allow_sys_shutdown=1):
    osd.clearscreen(color=osd.COL_BLACK)
    osd.drawstring('shutting down...', osd.width/2 - 90, osd.height/2 - 10,
                   fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
    osd.update()

    time.sleep(0.5)
    osd.shutdown() # SDL must be shutdown to restore video modes etc
    
    # XXX temporary kludge so it won't break on old config files
    if allow_sys_shutdown and 'ENABLE_SHUTDOWN_SYS' in dir(config):  
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
    os.system('killall -9 freevo_python 2&> /dev/null') 
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
        if menu_items[i].visible:
            items += [menu.MenuItem(menu_items[i].name, eval(menu_items[i].action),\
                                    menu_items[i].arg, eventhandler,
                                    None, 'main', menu_items[i].icon)]
            
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
                    mixer.setMainVolume(mainVolume)
                elif config.MAJOR_AUDIO_CTRL == 'PCM':
                    mixer.setPcmVolume(mainVolume)
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

    def move_tray(self, dir='toggle', notify=1):
        """Move the tray. dir can be toggle/open/close
        """

        if dir == 'toggle':
            if self.tray_open:
                dir = 'close'
            else:
                dir = 'open'

        if dir == 'open':
            if DEBUG: print 'Ejecting disc in drive %s' % self.drivename
            if notify:
                skin.PopupBox('Ejecting disc in drive %s' % self.drivename)
                osd.update()
            os.system('eject %s' % self.mountdir)
            self.tray_open = 1
            rc.post_event(rc.REFRESH_SCREEN)
        
        elif dir == 'close':
            if DEBUG: print 'Inserting %s' % self.drivename
            if notify:
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
        os.system('killall -9 freevo_python 2&> /dev/null') 
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
            # close the tray without popup message
            media.move_tray(dir='close', notify=0)
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
    except KeyboardInterrupt:
        print 'Shutdown by keyboard interrupt'
        # Shutdown the application
        shutdown(allow_sys_shutdown=0)

    except:
        print 'Crash!'
        try:
            tb = sys.exc_info()[2]
            fname, lineno, funcname, text = traceback.extract_tb(tb)[-1]
            
            for i in range(5, 0, -1):
                osd.clearscreen(color=osd.COL_BLACK)
                osd.drawstring('Freevo crashed!', 70, 70,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.drawstring('Filename: %s' % fname, 70, 130,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.drawstring('Lineno: %s' % lineno, 70, 160,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.drawstring('Function: %s' % funcname, 70, 190,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.drawstring('Text: %s' % text, 70, 220,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.drawstring('Please see the logfiles for more info', 70, 280,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                
                osd.drawstring('Exit in %s seconds' % i, 70, 340,
                               fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
                osd.update()
                time.sleep(1)
                
        except:
            pass
        traceback.print_exc()

        # Shutdown the application, but not the system even if that is
        # enabled
        shutdown(allow_sys_shutdown=0)
