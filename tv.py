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
import mplayer_tv

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
tvapp = mplayer_tv.get_singleton()


def start_tv(menuw=None, arg=None):
    mode = arg[0]
    channel = arg[1]
    tvapp.Play(mode, channel)
    

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

    local = time.localtime()
    weekday, hh, mm = local[6]+1, local[3], local[4]
    today_wday = str(weekday)
    today_hhmm = hh*100 + mm

    for channel in channels:
        # Only display active channels
        if DEBUG: print channel.displayname, channel.times
        if channel.times:
            displayit = FALSE
            for (days, start_time, stop_time) in channel.times:
                if today_wday in list(days):
                    if DEBUG: print "Channel timeinfo today"
                    if start_time <= today_hhmm <= stop_time:
                        displayit = TRUE
                        break # Out of for-loop
            if not displayit:
                continue  # Skip to next channel

        # Channel display name
        menu_str = '%s' % channel.displayname
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
                menu_str += ' \t%2d.%02d\t%s' % (hh, mm, p.title[:20])
        else:
            menu_str += '\tNO DATA'
            
        items += [menu.MenuItem(menu_str, start_tv,
                                ('tv', channel.tunerid), None, None, None, channel_logo)]
    
    hh = time.localtime(time.time())[3]
    mm = time.localtime(time.time())[4]
    
    mp3menu = menu.Menu('TV MENU  %02d:%02d' % (hh, mm), items)
    menuw.pushmenu(mp3menu)

    return
