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
# Revision 1.45  2004/11/04 19:55:48  dischi
# make it possible to schedule recordings for testing
#
# Revision 1.44  2004/10/23 15:19:32  rshortt
# Stub off some functions with Alerts.
#
# Revision 1.43  2004/10/23 14:38:13  rshortt
# Combine ProgramItem with what I had in channels.py, remove import of
# Favorite because it will be combined with FavoriteItem, added comments.
#
# Revision 1.42  2004/08/23 12:40:55  dischi
# remove osd.py dep
#
# Revision 1.41  2004/07/22 21:21:49  dischi
# small fixes to fit the new gui code
#
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
import gui

# import util.tv_util as tv_util
import tv.record_client as record_client
import event as em

from item import Item
from gui import AlertBox
from gui import InputBox
# from tv.record_types import Favorite

import recordings

DEBUG = config.DEBUG


class ProgramItem(Item):
    def __init__(self, title, start, stop, subtitle='', description='',
                 id=None, channel_id=None, context='guide', skin_type='video',
                 parent=None):
        if parent:
            Item.__init__(self, parent, skin_type=skin_type)
        else:
            Item.__init__(self, skin_type=skin_type)

        # TODO: deal with context 'guide' or 'scheduled' (find a different way)
        self.context = context

        self.title = self.info['title'] = title
        # self.info['title'] = title
        self.start = self.info['start'] = start
        self.stop = self.info['stop'] = stop
        
        # FIXME: after self.info['channel'] is fixed further below remove it
        #        from here.
        self.info['channel'] = self.channel_id = channel_id
        self.info['subtitle'] = subtitle
        self.info['description'] = description
        self.info['id'] = id
        self.name = '%d\t%s' % (self.info['start'], self.title)

        self.valid = 1
# we probably don't need the valid attribute anymore
# XXX: getting acsii error with if title == NO_DATA:
#        if title == NO_DATA:
#            self.valid = 0
#        else:
#            self.valid = 1

        # FIXME: add a hook here or another file to see if we're
        #        scheduled for recording
        self.scheduled  = False

        # FIXME: figure out if we want to keep this kind of close reference
        #        to individual programs matching a favorite.
        self.favorite = False

        # FIXME: fix tv_util.get_chan_displayname() or do it another way
        # self.info['channel'] = tv_util.get_chan_displayname(channel_id)

        self.start_str = time.strftime(config.TV_DATETIMEFORMAT,
                                       time.localtime(self.start))
        self.stop_str = time.strftime(config.TV_DATETIMEFORMAT,
                                      time.localtime(self.stop))

        # TODO: add category support (from epgdb)
        self.categories = ''
        #try:
        #    for cat in prog.categories:
        #        if prog.categories.index(cat) > 0:
        #            self.categories += ', %s' % cat
        #        else:
        #            self.categories += '%s' % cat
        #except AttributeError:
        #    pass
        
        # TODO: add ratings support (from epgdb)
        self.ratings = ''
        #try:
        #    for rat in prog.ratings.keys():
        #        self.ratings += '%s ' % rat
        #except:
        #    pass


    def __unicode__(self):
        """
        return as unicode for debug
        """
        bt = time.localtime(self.start)   # Beginning time tuple
        et = time.localtime(self.stop)    # End time tuple
        begins = '%s-%02d-%02d %02d:%02d' % (bt[0], bt[1], bt[2], bt[3], bt[4])
        ends   = '%s-%02d-%02d %02d:%02d' % (et[0], et[1], et[2], et[3], et[4])
        return u'%s to %s  %3s ' % (begins, ends, self.channel_id) + self.title


    def __str__(self):
        """
        return as string for debug
        """
        return String(self.__unicode__())


    def __cmp__(self, other):
        """
        compare function, return 0 if the objects are identical, 1 otherwise
        """
        if not other:
            return 1
        
        for attr in ['title', 'start', 'stop']:
            if not hasattr(other, attr):
                return 1

        return self.title != other.title or \
               self.start != other.start or \
               self.stop  != other.stop or \
               self.channel_id != other.channel_id


    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr == 'start':
            return Unicode(time.strftime(config.TV_TIMEFORMAT, time.localtime(self.start)))
        if attr == 'stop':
            return Unicode(time.strftime(config.TV_TIMEFORMAT, time.localtime(self.stop)))
        if attr == 'date':
            return Unicode(time.strftime(config.TV_DATEFORMAT, time.localtime(self.start)))
        if attr == 'time':
            return self.getattr('start') + u' - ' + self.getattr('stop')
        if hasattr(self, attr):
            return getattr(self,attr)
        return ''


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
        msg = 'WORK IN PROGRESS'
        AlertBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
        return

        # FIXME: combine Favorite and FavoriteItem
        # fav = Favorite(self.prog.title, self.prog, True, True, True, -1)
        # fav_item = FavoriteItem(self, fav, fav_action='add')
        # fav_item.display_favorite(menuw=menuw)


    def rem_favorite(self, arg=None, menuw=None):
        pass


    def find_more(self, arg=None, menuw=None):
        msg = 'WORK IN PROGRESS'
        AlertBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
        return

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
        (result, msg) = recordings.schedule_recording(self)
        if result:
            if menuw:
	        if self.context=='search':
                    menuw.delete_menu()
                    menuw.delete_menu()
                menuw.back_one_menu(arg='reload')
            AlertBox(text=_('"%s" has been scheduled for recording') % \
                     self.title).show()
        else:
            AlertBox(text=_('Scheduling Failed')+(': %s' % msg)).show()


    def remove_program(self, arg=None, menuw=None):
        msg = 'WORK IN PROGRESS'
        AlertBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
        return

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
                 width = gui.width - config.OSD_OVERSCAN_X - 20,
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




