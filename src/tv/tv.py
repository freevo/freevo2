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
# Revision 1.17  2003/08/20 22:29:37  gsbarbieri
# UPPER CASE TEXT IS UGLY! :)
#
# Revision 1.16  2003/08/03 11:10:26  dischi
# Added TVGUIDE_HOURS_PER_PAGE
#
# Revision 1.15  2003/07/13 19:46:21  rshortt
# Move the work portion of get_friendly_channel() into tv_util.
#
# Revision 1.14  2003/06/29 15:01:31  outlyer
# Display the channel's friendly (display name) in the tuner popupbox.
#
# Since XMLTV 0.6.11 uses what they call "RFC" channel names which are
# very long and don't reveal much about the channel.
#
# This will obviously have no regressive effect, since users had the
# friendly name before.
#
# Revision 1.13  2003/06/02 21:29:22  outlyer
# Changed the "Schedule Editor" to show up in the TV Submenu, along with "Guide" and
# "Recorded Shows" which makes a lot more sense then where it was before, which was
# also exceptionally well hidden.
#
# To do this properly, I also had to move record_schedule into a class, subclassing
# from Item, and so problems may and possibly will arise. I've tested it a little,
# but please bang on this, because while it's a relatively minor change, it does
# get things working inside the properly model, at least for a start.
#
# Bug reports are expected and welcome :)
#
# Revision 1.12  2003/04/24 19:56:42  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.11  2003/04/22 19:34:12  dischi
# mplayer and tvtime are now plugins
#
# Revision 1.10  2003/04/21 18:20:44  dischi
# make tv itself and not tv.tv the plugin (using __init__.py)
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
from gui.PopupBox import PopupBox

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

        guide = epg.get_guide(PopupBox(text='Preparing the program guide'))

        start_time = self.get_start_time()
        stop_time = self.get_start_time() + config.TVGUIDE_HOURS_PER_PAGE * 60 * 60

        channels = guide.GetPrograms(start=start_time+1, stop=stop_time-1)

        if not channels:
            AlertBox(text='TV Guide is corrupt!').show()
            return

        prg = None
        for chan in channels:
            if chan.programs:
                prg = chan.programs[0]
                break

        TVGuide(start_time, stop_time, guide.chan_list[0].id, prg, start_tv, menuw)
