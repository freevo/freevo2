#
# tv.py
#
# This is the Freevo TV module. 
#
# $Id$

import sys
#import random
import time, math
#, os, glob
#import string, popen2, fcntl, select, struct

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

# The Skin
import skin

# Extended Menu
import ExtendedMenu
sys.path.append('tv/')
import ExtendedMenu_TV



# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

# Set up the mixer
mixer = mixer.get_singleton()

# Set up the TV application
tvapp = mplayer_tv.get_singleton()

menuwidget = menu.get_singleton()

skin = skin.get_singleton()


# Set up the extended menu
view = ExtendedMenu_TV.ExtendedMenuView_TV()
info = ExtendedMenu_TV.ExtendedMenuInfo_TV()
listing = ExtendedMenu_TV.ExtendedMenuListing_TV()
em = ExtendedMenu_TV.ExtendedMenu_TV(view, info, listing)


def get_start_time():
    ttime = time.localtime()
    stime = [ ]
    for i in ttime:
        stime += [i]
    stime[5] = 0 # zero seconds
    if stime[4] >= 30:
        stime[4] = 30
    else:
        stime[4] = 0
    
    return time.mktime(stime)

# Set up some global variables
start_time = get_start_time()
stop_time = get_start_time()


def start_tv(mode=None, channel_id=None):

    tuner_id = get_tunerid(channel_id)
    
    print 'mode=%s    channel=%s  tuner=%s' % (mode, channel_id, tuner_id)
    
    tvapp.Play(mode, tuner_id)


def get_tunerid(channel_id):
    tuner_id = None
    for vals in config.TV_CHANNELS:
        tv_channel_id, tv_display_name, tv_tuner_id = vals[:3]
        if tv_channel_id == channel_id:
            return tv_tuner_id

    skin.PopupBox('Could not find TV channel %s' % channel_id)
    time.sleep(2)
    return None
    
   
def eventhandler(event):
    print 'TV %s' % event
    
    if event == rc.EXIT or event == rc.MENU:
        rc.app = None
        menuwidget.refresh()
    elif event == rc.SELECT or event == rc.PLAY:
        start_tv('tv', em.listing.last_to_listing[3].channel_id)
    else:
        em.eventhandler(event)


def refresh():
     em.refresh()


def main_menu(arg, menuw):
    if arg == 'record':
        start_tv(None, ('record', None))
        return

    rc.app = eventhandler

    skin.PopupBox('Preparing the program guide') 

    guide = epg.get_guide()
    
    start_time = get_start_time()
    stop_time = get_start_time() + 2 * 60 * 60

    channels = guide.GetPrograms(start=start_time+1, stop=stop_time-1)

    prg = None
    for chan in channels:
        if chan.programs:
            prg = chan.programs[0]
            break
        
    listing.ToListing([start_time, stop_time, guide.chan_list[0].id, prg])
    em.eventhandler(rc.UP)

    em.refresh()

