#
# tv.py
#
# This is the Freevo TV module. 
#
# $Id$

import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct

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

# The TV application
import v4l1tv

# The Electronic Program Guide
import epg_xmltv as epg

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

# Create the MenuWidget object
menuwidget = menu.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

# Set up the mixer
mixer = mixer.get_singleton()

# Set up the TV application
v4l1tv = v4l1tv.get_singleton()


def start_tv(menuw=None, arg=None):
    mode = arg[0]
    channel = arg[1]
    v4l1tv.Play(mode, channel)
    

def main_menu(arg, menuw):
    if arg == 'record':
        start_tv(None, ('record', None))
        return
    
    osd.clearscreen(color=osd.COL_BLACK)
    osd.drawstring('Getting the program guide', 30, 280,
                   fgcolor=osd.COL_ORANGE, bgcolor=0xff000000)
    osd.update()
    
    guide = epg.get_guide()

    osd.drawstring('Done!', 30, 320,
                   fgcolor=osd.COL_ORANGE, bgcolor=0xff000000)
    osd.update()
    
    items = []

    items += [menu.MenuItem('Last Channel', start_tv, ('tv', None))]
    items += [menu.MenuItem('VCR', start_tv, ('vcr', None))]

    # Get all programs from now until the end of the guide
    now = time.time()
    channels = guide.GetPrograms(start=now, stop=None)
    
    for channel in channels:
        # Channel display name
        menu_str = '%-10s ' % channel.displayname
        # Logo
	channel_logo = config.TV_LOGOS + '/' + channel.id + '.png'
	if not os.path.isfile(channel_logo):
            if DEBUG: print 'TV: Cannot find logo "%s"' % channel_logo
            channel_logo = None

        # Add the first two programs to the menu item
        if channel.programs:
            for p in channel.programs[:2]:
                hh = time.localtime(p.start)[3]
                mm = time.localtime(p.start)[4]
                menu_str += '%2d.%02d   %-20.20s    ' % (hh, mm, p.title)
        else:
            menu_str += 'NO DATA'
            
        items += [menu.MenuItem(menu_str, start_tv,
                                ('tv', channel.tunerid), None, None, channel_logo)]
    
    hh = time.localtime(time.time())[3]
    mm = time.localtime(time.time())[4]
    
    mp3menu = menu.Menu('TV MENU  %2d:%02d' % (hh, mm), items)
    menuw.pushmenu(mp3menu)

    return
