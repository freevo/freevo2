# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# ProgramDisplay - Information and actions for TvPrograms.
# -----------------------------------------------------------------------
# $Id$
#
# Todo: 
# Notes: 
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.40  2004/07/11 14:02:01  dischi
# prevent crash
#
# Revision 1.39  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.38  2004/06/23 12:18:54  outlyer
# More crashe fixes for assumed variables that don't exist.
#
# Revision 1.37  2004/05/28 23:38:21  mikeruelle
# better backoff so we do not see intermediate menu
#
# Revision 1.36  2004/05/27 01:04:37  mikeruelle
# fix bug with search for more like this. need better stack pop but this
# fixes things for now.
#
# -----------------------------------------------------------------------
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
from time import gmtime, strftime

import plugin, config, menu
import osd

import util.tv_util as tv_util
import tv.record_client as record_client
import event as em

from item import Item
from gui.AlertBox import AlertBox
from gui.InputBox import InputBox
from tv.record_types import Favorite

DEBUG = config.DEBUG


class ProgramItem(Item):
    def __init__(self, parent, prog, context='guide'):
        Item.__init__(self, parent, skin_type='video')
        self.prog = prog
        self.context = context

        self.name = self.title = prog.title
        if hasattr(prog,'sub_title'): self.sub_title = prog.sub_title
        if hasattr(prog,'desc'): self.desc = prog.desc
        self.channel = tv_util.get_chan_displayname(prog.channel_id)

        if hasattr(prog, 'scheduled'):
            self.scheduled = prog.scheduled
        else:
            self.scheduled = False
        self.favorite = False

        self.start = time.strftime(config.TV_DATETIMEFORMAT,
                                   time.localtime(prog.start))
        self.stop = time.strftime(config.TV_DATETIMEFORMAT,
                                       time.localtime(prog.stop))

        self.categories = ''
        try:
            for cat in prog.categories:
                if prog.categories.index(cat) > 0:
                    self.categories += ', %s' % cat
                else:
                    self.categories += '%s' % cat
        except AttributeError:
            pass
        
        self.ratings = ''
        try:
            for rat in prog.ratings.keys():
                self.ratings += '%s ' % rat
        except:
            pass


    def actions(self):
        return [( self.display_program , _('Display program') )]


    def display_program(self, arg=None, menuw=None):
        items = []

        (got_schedule, schedule) = record_client.getScheduledRecordings()
        if got_schedule:
            (result, message) = record_client.isProgScheduled(self.prog, 
                                                              schedule.getProgramList())
            if result:
                self.scheduled = True

        if self.scheduled:
	    items.append(menu.MenuItem(_('Remove from schedule'), 
                                       action=self.remove_program))
        else:
	    items.append(menu.MenuItem(_('Schedule for recording'), 
                                       action=self.schedule_program))

        if self.context != 'search':
            items.append(menu.MenuItem(_('Search for more of this program'), 
                                       action=self.find_more))

        (got_favs, favs) = record_client.getFavorites()
        if got_favs:
            (result, junk) = record_client.isProgAFavorite(self.prog, favs)
            if result:
                self.favorite = True

        if self.favorite:
            items.append(menu.MenuItem(_('Remove from favorites'), 
                                       action=self.rem_favorite))
        else:
            items.append(menu.MenuItem(_('Add to favorites'), 
                                       action=self.add_favorite))

        program_menu = menu.Menu(_('Program Menu'), items, 
                                 item_types = 'tv program menu')
        program_menu.infoitem = self
        menuw.pushmenu(program_menu)
        menuw.refresh()


    def add_favorite(self, arg=None, menuw=None):
        fav = Favorite(self.prog.title, self.prog, True, True, True, -1)
        fav_item = FavoriteItem(self, fav, fav_action='add')
        fav_item.display_favorite(menuw=menuw)


    def rem_favorite(self, arg=None, menuw=None):
        pass


    def find_more(self, arg=None, menuw=None):
        # XXX: The searching part of this function could probably be moved
	#      into a util module or record_client itself.
        _debug_(String('searching for: %s' % self.prog.title))

        pop = AlertBox(text=_('Searching, please wait...'))
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
        menuw.pushmenu(search_menu)
        menuw.refresh()


    def schedule_program(self, arg=None, menuw=None):
        (result, msg) = record_client.scheduleRecording(self.prog)
        if result:
            if menuw:
	        if self.context=='search':
                    menuw.delete_menu()
                    menuw.delete_menu()
                menuw.back_one_menu(arg='reload')
            AlertBox(text=_('"%s" has been scheduled for recording') % \
                     self.prog.title).show()
        else:
            AlertBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
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
            AlertBox(text=_('Remove Failed')+(': %s' % msg)).show()



class FavoriteItem(Item):
    def __init__(self, parent, fav, fav_action='edit'):
        Item.__init__(self, parent, skin_type='video')
        self.fav   = fav
        self.name  = self.origname = fav.name
        self.title = fav.title
        self.fav_action = fav_action

        self.week_days = (_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun'))

        if fav.channel == 'ANY':
            self.channel = _('ANY CHANNEL')
        else:
            self.channel = fav.channel
        if fav.dow == 'ANY':
            self.dow = _('ANY DAY')
        else:
            self.dow = self.week_days[int(fav.dow)]
        if fav.mod == 'ANY':
            self.mod = _('ANY TIME')
        else:
            self.mod = strftime(config.TV_TIMEFORMAT, gmtime(float(fav.mod * 60)))

        # needed by the inputbox handler
        self.menuw = None


    def actions(self):
        return [( self.display_favorite , _('Display favorite') )]


    def display_favorite(self, arg=None, menuw=None):
        items = []

        items.append(menu.MenuItem(_('Modify name'), action=self.mod_name))
        items.append(menu.MenuItem(_('Modify channel'), action=self.mod_channel))
        items.append(menu.MenuItem(_('Modify day of week'), action=self.mod_day))
        items.append(menu.MenuItem(_('Modify time of day'), action=self.mod_time))

        # XXX: priorities aren't quite supported yet
        if 0:
            (got_favs, favs) = record_client.getFavorites()
            if got_favs and len(favs) > 1:
                items.append(menu.MenuItem(_('Modify priority'), 
                                           action=self.mod_priority))

        items.append(menu.MenuItem(_('Save changes'), action=self.save_changes))
        items.append(menu.MenuItem(_('Remove favorite'), action=self.rem_favorite))

        favorite_menu = menu.Menu(_('Favorite Menu'), items, 
                                 item_types = 'tv favorite menu')
        favorite_menu.infoitem = self
        menuw.pushmenu(favorite_menu)
        menuw.refresh()


    def mod_name(self, arg=None, menuw=None):
        self.menuw = menuw
        InputBox(text=_('Alter Name'), handler=self.alter_name,
                 width = osd.get_singleton().width - config.OSD_OVERSCAN_X - 20,
                 input_text=self.name).show()


    def alter_name(self, name):
        if name:
            self.name = self.fav.name = name

        self.menuw.refresh()


    def mod_channel(self, arg=None, menuw=None):
        items = []

        items.append(menu.MenuItem('ANY CHANNEL', action=self.alter_prop,
                     arg=('channel', 'ANY')))

        for chanline in config.TV_CHANNELS:
            items.append(menu.MenuItem(chanline[1], action=self.alter_prop,
                         arg=('channel', chanline[1])))

        favorite_menu = menu.Menu(_('Modify Channel'), items, 
                                  item_types = 'tv favorite menu')
        favorite_menu.infoitem = self
        menuw.pushmenu(favorite_menu)
        menuw.refresh()


    def alter_prop(self, arg=(None,None), menuw=None):
        (prop, val) = arg

        if prop == 'channel':
            if val == 'ANY':
                self.channel = 'ANY CHANNEL'
                self.fav.channel = 'ANY'
            else:
                self.channel = val
                self.fav.channel = val

        elif prop == 'dow':
            if val == 'ANY':
                self.dow = 'ANY DAY'
                self.fav.dow = 'ANY'
            else:
                self.dow = self.week_days[val]
                self.fav.dow = val

        elif prop == 'mod':
            if val == 'ANY':
                self.mod = 'ANY TIME'
                self.fav.mod = 'ANY'
            else:
                # self.mod = tv_util.minToTOD(val)
                self.mod = strftime(config.TV_TIMEFORMAT, 
                                    gmtime(float(val * 60)))
                self.fav.mod = val

        if menuw:  
            menuw.back_one_menu(arg='reload')


    def mod_day(self, arg=None, menuw=None):
        items = []

        items.append(menu.MenuItem('ANY DAY', action=self.alter_prop,
                     arg=('dow', 'ANY')))

        for i in range(len(self.week_days)):
            items.append(menu.MenuItem(self.week_days[i], action=self.alter_prop,
                         arg=('dow', i)))

        favorite_menu = menu.Menu(_('Modify Day'), items, 
                                  item_types = 'tv favorite menu')
        favorite_menu.infoitem = self
        menuw.pushmenu(favorite_menu)
        menuw.refresh()


    def mod_time(self, arg=None, menuw=None):
        items = []

        items.append(menu.MenuItem('ANY TIME', action=self.alter_prop,
                     arg=('mod', 'ANY')))

        for i in range(48):
            mod = i * 30 
            items.append(menu.MenuItem(strftime(config.TV_TIMEFORMAT, 
                                                gmtime(float(mod * 60))), 
                                       action=self.alter_prop,
                                       arg=('mod', mod)))

        favorite_menu = menu.Menu(_('Modify Time'), items, 
                                  item_types = 'tv favorite menu')
        favorite_menu.infoitem = self
        menuw.pushmenu(favorite_menu)
        menuw.refresh()


    def save_changes(self, arg=None, menuw=None):
        if self.fav_action == 'edit':
            (result, msg) = record_client.removeFavorite(self.origname)
        else:
            result = True

        if result:
            (result, msg) = record_client.addEditedFavorite(self.fav.name, 
                                                            self.fav.title, 
                                                            self.fav.channel, 
                                                            self.fav.dow, 
                                                            self.fav.mod, 
                                                            self.fav.priority)
            if not result:
                AlertBox(text=_('Save Failed, favorite was lost')+(': %s' % msg)).show()
            else:
                self.fav_action = 'edit'
                if menuw:  
                    menuw.back_one_menu(arg='reload')

        else:
            AlertBox(text=_('Save Failed')+(': %s' % msg)).show()


    def rem_favorite(self, arg=None, menuw=None):
        if self.fav_action == 'add':
            AlertBox(text=_('Favorite not added yet.')).show()
            return
       
        (result, msg) = record_client.removeFavorite(self.origname)
        if result:
            # then menu back one which should show an updated list if we
            # were viewing favorites or back to the program display
	    # or refresh the program menu with remove option instead of add
            if menuw:  
                menuw.back_one_menu(arg='reload')

        else:
            AlertBox(text=_('Remove Failed')+(': %s' % msg)).show()




