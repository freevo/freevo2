#!/usr/bin/env python
#-----------------------------------------------------------------------
# ProgramDisplay - Information and actions for TvPrograms.
#-----------------------------------------------------------------------
# $Id$
#
# Todo: 
# Notes: 
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.27  2004/02/23 03:43:23  rshortt
# Ditch the popup-gui style in favour of a faster and more freevo-like menu.
#
#
#
#-----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------

import time, traceback

import plugin, config, menu

import util.tv_util as tv_util
import tv.record_client as record_client
import event as em

from item import Item
from gui.PopupBox  import *
from gui.AlertBox  import *

DEBUG = config.DEBUG


class ProgramItem(Item):
    def __init__(self, parent, prog, context='guide'):
        Item.__init__(self, parent, skin_type='video')
        self.prog = prog
        self.context = context

        self.name = self.title = prog.title
        self.sub_title = prog.sub_title
        self.desc = prog.desc
        self.channel = tv_util.get_chan_displayname(prog.channel_id)

        if hasattr(prog, 'scheduled'):
            self.scheduled = prog.scheduled
        else:
            self.scheduled = False

        self.start = time.strftime(config.TV_DATETIMEFORMAT,
                                   time.localtime(prog.start))
        self.stop = time.strftime(config.TV_DATETIMEFORMAT,
                                       time.localtime(prog.stop))

        self.categories = ''
        for cat in prog.categories:
            if prog.categories.index(cat) > 0:
                self.categories += ', %s' % cat
            else:
                self.categories += '%s' % cat

        self.ratings = ''
        for rat in prog.ratings.keys():
            self.ratings += '%s ' % rat


    def actions(self):
        return [( self.display_program , 'Display program' )]


    def display_program(self, arg=None, menuw=None):
        items = []
        if self.context == 'schedule':
	    items.append(menu.MenuItem(_('Remove from schedule'), 
                                       action=self.remove_program))
        elif self.context == 'guide':
	    items.append(menu.MenuItem(_('Schedule for recording'), 
                                       action=self.schedule_program))

        if self.context != 'search':
            items.append(menu.MenuItem(_('Search for more of this program'), 
                                       action=self.find_more))

        items.append(menu.MenuItem(_('Add to favorites'), 
                                   action=self.add_favorite))

        program_menu = menu.Menu(_('Program Menu'), items, 
                                 item_types = 'tv program menu')
        rc.app(None)
        program_menu.infoitem = self
        menuw.pushmenu(program_menu)
        menuw.refresh()


    def add_favorite(self, arg=None, menuw=None):
        pass


    def find_more(self, arg=None, menuw=None):
        # XXX: The searching part of this function could probably be moved
	#      into a util module or record_client itself.
        _debug_('searching for: %s' % self.prog.title)

        pop = PopupBox(text=_('Searching, please wait...'))
        pop.show()

        items = []
        (result, matches) = record_client.findMatches(self.prog.title)
                             
        pop.destroy()
        if result:
            _debug_('search found %s matches' % len(matches))

            f = lambda a, b: cmp(a.start, b.start)
            matches.sort(f)
            for prog in matches:
               items.append(ProgramItem(self, prog, context='search'))
        else:
	    if matches == 'no matches':
                AlertBox(text=_('No matches found for %s') % self.prog.title).show()
                return
            AlertBox(text=_('findMatches failed: %s') % matches).show()
            return

        search_menu = menu.Menu(_( 'Search Results' ), items,
                                item_types = 'tv program menu')
        rc.app(None)
        menuw.pushmenu(search_menu)
        menuw.refresh()


    def schedule_program(self, arg=None, menuw=None):
        (result, msg) = record_client.scheduleRecording(self.prog)
        if result:
            AlertBox(text=_('"%s" has been scheduled for recording') % \
                     self.prog.title).show()
            if menuw:  
                menuw.back_one_menu(arg='reload')
        else:
            AlertBox(text=_('Scheduling Failed: %s') % msg).show()
        # then menu back one or refresh the menu with remove option
	# instead of schedule


    def remove_program(self, arg=None, menuw=None):
        (result, msg) = record_client.removeScheduledRecording(self.prog)
        if result:
            # then menu back one which should show an updated list if we
            # were viewing scheduled recordings or back to the guide and
            # update the colour of the program we selected.
	    # or refresh the menu with remove option instead of schedule
            if menuw:  
                menuw.back_one_menu(arg='reload')

        else:
            AlertBox(text=_('Remove Failed: %s') % msg).show()




