#if 0 /*
# -----------------------------------------------------------------------
# tv.py - This is the Freevo TV module. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/11/24 13:58:45  dischi
# code cleanup
#
#
# -----------------------------------------------------------------------
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
# ----------------------------------------------------------------------- */
#endif


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
import mplayer

# The Electronic Program Guide
import epg_xmltv as epg

# The Skin
import skin

# Extended Menu
import ExtendedMenu
import ExtendedMenu_TV

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

# Set up the mixer
mixer = mixer.get_singleton()

# Set up the TV application
tvapp = mplayer.get_singleton()

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
    #print 'TV %s' % event
    
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

    # Check that the TV channel list is not None
    if not config.TV_CHANNELS:
        msg = 'The list of TV channels is invalid!\n'
        msg += 'Please check the config file.'
        skin.PopupBox(msg)
        time.sleep(3.0)
        menuwidget.refresh()
        return
    
    if arg == 'record':
        start_tv(None, ('record', None))
        return

    skin.PopupBox('Preparing the program guide') 

    guide = epg.get_guide()
    
    start_time = get_start_time()
    stop_time = get_start_time() + 2 * 60 * 60

    channels = guide.GetPrograms(start=start_time+1, stop=stop_time-1)

    if not channels:
        menuwidget.refresh()
        skin.PopupBox('TV Guide is corrupt!')
	time.sleep(3.0)
	menuwidget.refresh()
	return

    rc.app = eventhandler

    prg = None
    for chan in channels:
        if chan.programs:
            prg = chan.programs[0]
            break
        
    listing.ToListing([start_time, stop_time, guide.chan_list[0].id, prg])
    em.eventhandler(rc.UP)

    em.refresh()

