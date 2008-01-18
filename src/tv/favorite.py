# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# favorite.py -
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rob@tvcentric.com>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#                Rob Shortt <rob@tvcentric.com>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
# -----------------------------------------------------------------------------

# python imports
import re
import time

# kaa imports
import kaa.epg
from kaa.strutils import unicode_to_str

# freevo ui imports
from freevo.ui import config

# freevo core imports
import freevo.ipc

# freevo imports
from freevo.ui.menu import Item, Action, ActionItem, Menu
from freevo.ui.application import MessageWindow
from freevo.ui.tv.program import ProgramItem

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

DAY_NAMES = [_('Sun'), _('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat')]

#Define the time slots (when chnaging the time) in minutes
TIME_SLOTS = 10
TIME_RANGE = (1440 / TIME_SLOTS)

class FavoriteItem(Item):
    """
    A favorite item to add/delete/change a favorite for the recordserver.
    """

    def __init__(self, parent, fav):
        Item.__init__(self, parent)

        self.new = True
        self.id = 0
        self.start = float(0)
        self.stop = float(1440*60)-1

        if isinstance(fav, ProgramItem):
            #check if already a favorite
            f = tvserver.favorites.get(fav.title, fav.channel, fav.start, fav.stop)
            if not f:
                # create from ProgramItem
                # Convert to 0=Sunday - 6=Saterday
                day = min(time.localtime(fav.start)[6] + 1, 6)
                self.days = [ day ]
                self.name = self.title = fav.title
                self.channels = [ fav.channel]
            else:
                # there is already a existing ipc Favorite object
                fav = f
        if isinstance(fav, freevo.ipc.tvserver.Favorite):
            # created with ipc Favorite object
            self.name = self.title = fav.title
            self.days = fav.days
            self.channels = fav.channels
            self.new = False
            self.id = fav.id
            for t in fav.times:
                self.start, self.stop = self._str_to_time(t)


    def get_start(self):
        """
        Return start time as formated unicode string.
        """
        return unicode(time.strftime(config.tv.timeformat, time.localtime(self.start)))


    def get_stop(self):
        """
        Return stop time as formated unicode string.
        """
        return unicode(time.strftime(config.tv.timeformat, time.localtime(self.stop)))


    def get_time(self):
        """
        Return start time and stop time as formated unicode string.
        """
        return self.get_start + u' - ' + self.get_stop()


    def get_date(self):
        """
        Return day(s) of week as formated unicode string.
        """
        if self.days == 'ANY':
            return _('ANY')
        return ', '.join(['%s' % DAY_NAMES[d] for d in self.days])


    def get_channel(self):
        """
        Return channel(s) for this favorite.
        """
        if self.channels == 'ANY':
            return _('ANY')
        return ', '.join(['%s' % chan for chan in self.channels])


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        return [ Action(_('Show favorite menu'), self.submenu) ]


    def submenu(self):
        """
        show a submenu for this item
        """
        items = []

        if self.new:
            items.append(ActionItem(_('Add favorite'), self, self.add))
        else:
            items.append(ActionItem(_('Remove favorite'), self, self.remove))

        items.append(ActionItem(_('Change day'), self, self.change_days))
        items.append(ActionItem(_('Change channel'), self, self.change_channels))
        action = ActionItem(_('Change start time'), self, self.change_time)
        action.parameter('start')
        items.append(action)
        action = ActionItem(_('Change stop time'), self, self.change_time)
        action.parameter('stop')
        items.append(action)

        s = Menu(self, items, type = 'tv favorite menu')
        s.submenu = True
        s.infoitem = self
        self.get_menustack().pushmenu(s)


    @kaa.yield_execution()
    def add(self):
        result = tvserver.favorites.add(self.title, self.channels, self.days,
                                        [self._time_to_str()], 50, False)
        if isinstance(result, kaa.InProgress):
            yield result
            result = result()
        if result != tvserver.favorites.SUCCESS:
            text = _('Adding favorite Failed')+(': %s' % result)
        else:
            text = _('"%s" has been added to your favorites') % self.title
        MessageWindow(text).show()
        self.get_menustack().back_one_menu()


    @kaa.yield_execution()
    def remove(self):
        result = tvserver.favorites.remove(self.id)
        if isinstance(result, kaa.InProgress):
            yield result
            result = result()
        if result != tvserver.favorites.SUCCESS:
            text = _('Remove favorite Failed')+(': %s' % result)
        else:
            text = _('"%s" has been removed from you favorites') % self.title
            MessageWindow(text).show()
        self.get_menustack().back_one_menu()

    @kaa.yield_execution()
    def modify(self, info):
        result = tvserver.favorites.modify(self.id, info)
        if isinstance(result, kaa.InProgress):
            yield result
            result = result()
        if result != tvserver.favorites.SUCCESS:
            text = _('Modified favorite Failed')+(': %s' % result)
            MessageWindow(text).show()

    def change_days(self):
        items = []
        action = ActionItem('ANY', self, self.handle_change)
        action.parameter('days', 'ANY')
        items.append(action)
        for dayname in DAY_NAMES:
            action = ActionItem(dayname, self, self.handle_change)
            action.parameter('days', dayname)
            items.append(action)

        s = Menu(self, items, type = 'tv favorite menu')
        s.submenu = True
        s.infoitem = self
        self.get_menustack().pushmenu(s)

    def change_channels(self):
        items = []
        action = ActionItem('ANY', self, self.handle_change)
        action.parameter('channels', 'ANY')
        items.append(action)

        list = kaa.epg.get_channels(sort=True)
        for chan in list:
            action = ActionItem(chan.name, self, self.handle_change)
            action.parameter('channels', chan.name)
            items.append(action)

        s = Menu(self, items, type = 'tv favorite menu')
        s.submenu = True
        s.infoitem = self
        self.get_menustack().pushmenu(s)

    def change_time(self, startstop):
        items = []
        action = ActionItem('ANY', self, self.handle_change)
        action.parameter(startstop, 'ANY')
        items.append(action)
        if startstop == 'start':
            starttime = self.start
        else:
            starttime = self.stop - (self.stop % (TIME_SLOTS * 60))
        for i in range(TIME_RANGE):
            newtime = float( (i * TIME_SLOTS * 60) + starttime) % (1440 * 60)
            showtime = unicode(time.strftime(config.tv.timeformat,
                                     time.gmtime(newtime)))
            action = ActionItem(showtime, self, self.handle_change)
            action.parameter(startstop, newtime)
            items.append(action)

        s = Menu(self, items, type = 'tv favorite menu')
        s.submenu = True
        s.infoitem = self
        self.get_menustack().pushmenu(s)

    def handle_change(self, item, value):

        info = None
        infovalue = None
        if item == 'days':
            info = 'days'
            if value == 'ANY':
                self.days = [0, 1, 2, 3, 4, 5, 6]
            else:
                self.days = [DAY_NAMES.index(value)]
            infovalue = self.days
        if item == 'channels':
            info = 'channels'
            if value == 'ANY':
                self.channels = []
                list = kaa.epg.get_channels(sort=True)
                for chan in list:
                    self.channels.append(chan.name)
            else:
                self.channels = [value]
            infovalue = self.channels
        if item == 'start':
            info = 'times'
            if value == 'ANY':
                self.start = float(0)
                self.stop = float(1440*60)-1
            else:
                self.start = value
            infovalue = [self._time_to_str()]
        if item == 'stop':
            info = 'times'
            if value == 'ANY':
                self.start = float(0)
                self.stop = float(1440*60)-1
            else:
                self.stop = value
            infovalue = [self._time_to_str()]

        if not self.new:
            self.modify([(info, infovalue)])

        self.get_menustack().back_one_menu()

    def _time_to_str(self):
        start = time.strftime('%H:%M', time.gmtime(self.start))
        stop = time.strftime('%H:%M', time.gmtime(self.stop))
        return start + '-' + stop

    def _str_to_time(self, t):
        # internal regexp for time format
        _time_re = re.compile('([0-9]*):([0-9]*)-([0-9]*):([0-9]*)')

        m = _time_re.match(t).groups()
        start = float(m[0])*3600 + float(m[1])*60
        stop  = float(m[2])*3600 + float(m[3])*60

        return start, stop
