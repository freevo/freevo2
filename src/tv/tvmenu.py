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
# Revision 1.13  2004/02/04 14:11:18  outlyer
# Cleanup and fixup:
#
# o Now uses the mplayer OSD to show channel information when changing channels,
#     or you press the 'display' key.
# o Removed many old CVS log messages
# o Removed many debug-related 'print' statements
#
# Revision 1.12  2004/01/11 15:44:01  dischi
# changed menu display type to 'x main menu'
#
# Revision 1.11  2004/01/09 02:10:00  rshortt
# Patch from Matthieu Weber to revive add/edit favorites support from the
# TV interface.
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

import plugin

import util.tv_util as tv_util

# The Electronic Program Guide
import tv.epg_xmltv

from item import Item

from tv.tvguide import TVGuide
from directory import DirItem

from gui.AlertBox import AlertBox
from gui.PopupBox import PopupBox

import tv.program_display, tv.program_search, tv.view_favorites

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


def get_tunerid(channel_id):
    tuner_id = None
    for vals in config.TV_CHANNELS:
        tv_channel_id, tv_display_name, tv_tuner_id = vals[:3]
        if tv_channel_id == channel_id:
            return tv_tuner_id

    AlertBox(text=_('Could not find TV channel %s') % channel_id).show()
    return None


def get_friendly_channel(channel_id):
    channel_name = tv_util.get_chan_displayname(channel_id)

    if not channel_name: 
        AlertBox(text=_('Could not find TV channel %s') % channel_id).show()

    return channel_name


def start_tv(mode=None, channel_id=None):
    tuner_id = get_tunerid(channel_id)
    plugin.getbyname(plugin.TV).Play(mode, tuner_id)



#
# The TV menu
#
class TVMenu(Item):
    
    def __init__(self):
        Item.__init__(self)
        self.type = 'tv'


    def main_menu(self, arg, menuw):
        items = []
        if config.TV_CHANNELS:
            items.append(menu.MenuItem(_('TV Guide'), action=self.start_tvguide))
        if 0:
            items.append(menu.MenuItem(_('View VCR Input'), action=self.start_vcr))
        items.append(DirItem(config.TV_RECORD_DIR, None, name = _('Recorded Shows'),
                             display_type='tv'))
        items.append(menu.MenuItem(_('Scheduled Recordings'), 
                                   action=self.view_schedule))
        items.append(menu.MenuItem(_('Search Guide'), action=self.show_search))
        items.append(menu.MenuItem('View Favorites', action=self.show_favorites))

        plugins_list = plugin.get('mainmenu_tv')
        for p in plugins_list:
            items += p.items(self)

        menuw.pushmenu(menu.Menu(_('TV Main Menu'), items, item_types = 'tv main menu'))


    def show_search(self, arg, menuw):
        tv.program_search.ProgramSearch().show()
        return


    def show_favorites(self, arg, menuw):
        tv.view_favorites.ViewFavorites().show()
        return


    def view_schedule(self, arg, menuw):
        tv.program_display.ScheduledRecordings().show()
        return


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
            msg = _('The list of TV channels is invalid!\n')
            msg += _('Please check the config file.')
            AlertBox(text=msg).show()
            return

        if arg == 'record':
            start_tv(None, ('record', None))
            return

        TVGuide(self.get_start_time(), start_tv, menuw)


    def start_vcr(self, arg, menuw):
        _debug_('tvmenu: mode=vcr')
        plugin.getbyname(plugin.TV).Play('vcr', None)
