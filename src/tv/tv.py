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
# Revision 1.9  2003/04/20 12:43:34  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.8  2003/04/20 10:55:41  dischi
# mixer is now a plugin, too
#
# Revision 1.7  2003/04/17 04:44:11  krister
# Added a quick hack to support tvtime. It uses stdin on tvtime for commands, this is not supported in tvtime yet.
#
# Revision 1.6  2003/04/15 20:02:06  dischi
# use the plugin interface
#
# Revision 1.5  2003/04/06 21:12:58  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
#
# Revision 1.4  2003/03/30 16:27:05  dischi
# fixed a bug when changing skin at runtime
#
# Revision 1.3  2003/03/29 21:49:54  dischi
# Added new tv main menu for the new skin. This includes the tv guide
# (file is now called tvguide and not tvmenu) and DIR_RECORD. This
# directory is sort by date and can have a different menu style in the skin.
# See blue_round2 as example: there is a tv watermark, no view area and
# the listing area is larger.
#
# Revision 1.2  2003/03/08 17:40:42  dischi
# integration of the tv guide
#
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


import time
import os

from plugin import MainMenuPlugin

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# The menu widget class
import menu

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# The TV application
import mplayer
import tvtime

# The Electronic Program Guide
import epg_xmltv as epg

from item import Item

from tvguide import TVGuide
from directory import DirItem

from gui.AlertBox import AlertBox
from gui.PopupBox import PopupBox

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

# Set up the TV application
# Select MPlayer by default, tvtime is work in progress
if 1:
    tvapp = mplayer.get_singleton()
else:
    tvapp = tvtime.get_singleton()



#
# Plugin interface to integrate the tv module into Freevo
#
class PluginInterface(MainMenuPlugin):

    def items(self, parent):
        import skin

        skin = skin.get_singleton()
        menu_items = skin.settings.mainmenu.items

        icon = ""
        if menu_items['tv'].icon:
            icon = os.path.join(skin.settings.icon_dir, menu_items['tv'].icon)
        return ( menu.MenuItem(menu_items['tv'].name, icon=icon,
                               action=TVMenu().main_menu, type='main',
                               image=menu_items['tv'].image, parent=parent), )



def get_tunerid(channel_id):
    tuner_id = None
    for vals in config.TV_CHANNELS:
        tv_channel_id, tv_display_name, tv_tuner_id = vals[:3]
        if tv_channel_id == channel_id:
            return tv_tuner_id

    AlertBox(text='Could not find TV channel %s' % channel_id).show()
    return None


def start_tv(mode=None, channel_id=None):
    tuner_id = get_tunerid(channel_id)
    print 'mode=%s    channel=%s  tuner=%s' % (mode, channel_id, tuner_id)
    tvapp.Play(mode, tuner_id)



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
                          display_type='tv') ]

        menuw.pushmenu(menu.Menu('TV MAIN MENU', items, item_types = 'tv'))


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
        stop_time = self.get_start_time() + 2 * 60 * 60

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



