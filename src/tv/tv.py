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
# Revision 1.19  2003/08/25 18:44:32  dischi
# Moved HOURS_PER_PAGE into the skin fxd file, default=2
#
# Revision 1.18  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
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


import time

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# The menu widget class
import menu

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

import tv_util

# The Electronic Program Guide
import epg_xmltv as epg

from item import Item

from tvguide import TVGuide
from directory import DirItem

from gui.AlertBox import AlertBox

import record_schedule

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

import plugin

from record_schedule import ScheduleEdit

m = ScheduleEdit()


def get_tunerid(channel_id):
    tuner_id = None
    for vals in config.TV_CHANNELS:
        tv_channel_id, tv_display_name, tv_tuner_id = vals[:3]
        if tv_channel_id == channel_id:
            return tv_tuner_id

    AlertBox(text='Could not find TV channel %s' % channel_id).show()
    return None

def get_friendly_channel(channel_id):
    channel_name = tv_util.get_chan_displayname(channel_id)

    if not channel_name: 
        AlertBox(text='Could not find TV channel %s' % channel_id).show()

    return channel_name


def start_tv(mode=None, channel_id=None):
    tuner_id = get_tunerid(channel_id)
    print 'mode=%s    channel=%s  tuner=%s' % (mode, channel_id, tuner_id)
    plugin.getbyname(plugin.TV).Play(mode, tuner_id)



#
# The TV menu
#
class TVMenu(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.type = 'tv'


    def main_menu(self, arg, menuw):
        items = [ menu.MenuItem('TV Guide', action=self.start_tvguide),
                  DirItem(config.DIR_RECORD, None, name = 'Recorded Shows',
                          display_type='tv'),
                  menu.MenuItem('Scheduled Recordings',action=self.view_schedule)       ]
        menuw.pushmenu(menu.Menu('TV Main Menu', items, item_types = 'tv'))


    def get_start_time(self):
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

    def view_schedule(self,arg, menuw):
        m.main_menu()
        return

    def start_tvguide(self, arg, menuw):

        # Check that the TV channel list is not None
        if not config.TV_CHANNELS:
            msg = 'The list of TV channels is invalid!\n'
            msg += 'Please check the config file.'
            AlertBox(text=msg).show()
            return

        if arg == 'record':
            start_tv(None, ('record', None))
            return

        TVGuide(self.get_start_time(), start_tv, menuw)
