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
import epg

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
    v4l1tv.play(mode, channel)
    

def main_menu(arg, menuw):
    if arg == 'record':
        start_tv(None, ('record', None))
        return
    
    osd.clearscreen(color=osd.COL_BLACK)
    osd.drawstring('xxx', 'Getting the program guide', 30, 280,
                   fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
    
    guide = epg.get_guide()

    osd.drawstring('xxx', 'Done!', 30, 320,
                   fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
    
    items = []

    items += [menu.MenuItem('Last Channel', start_tv, ('tv', None))]
    items += [menu.MenuItem('VCR', start_tv, ('vcr', None))]

    for channel in guide.programs:
        # Get the channel number and name from the first entry
        p = channel[0]
        menu_str = '%3d %-7s ' % (p[0], p[1])

        for p in channel[0:2]:
            hh = time.localtime(p[3])[3]
            mm = time.localtime(p[3])[4]

            menu_str += '%2d.%02d   %-20.20s    ' % (hh, mm, p[2])

        items += [menu.MenuItem(menu_str, start_tv, ('tv', str(p[0])))]
    
    hh = time.localtime(time.time())[3]
    mm = time.localtime(time.time())[4]
    
    mp3menu = menu.Menu('TV MENU  %2d:%02d' % (hh, mm), items)
    menuw.pushmenu(mp3menu)

    return
