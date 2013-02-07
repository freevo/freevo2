# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Show images by date
# -----------------------------------------------------------------------------
# This plugin let the user browse the images by date. It does not look
# so nice on the GUI right now but shows the power of beacon.
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2013 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
import time

# kaa imports
import kaa
import kaa.beacon

# freevo imports
from ... import core as freevo


class BeaconQueryItem(freevo.Item):
    """
    Base item for all items in this plugin.
    """

    media_type = 'image'

    def __init__(self, name, parent, sample=None):
        super(BeaconQueryItem, self).__init__(parent)
        self.name = name
        if sample:
            self.info['thumbnail'] = sample.get('thumbnail')

    def _query(self, start, stop, **query):
        """
        Query beacon for images between start and stop dates
        """
        s1 = time.mktime((start[0], start[1], start[2], 0, 0, 0, -1, -1, -1))
        s2 = time.mktime((stop[0], stop[1], stop[2], 23, 59, 59, -1, -1, -1))
        q = kaa.beacon.QExpr('range', (s1, s2))
        return kaa.beacon.query(timestamp=q, type='image', **query)

    @kaa.coroutine()
    def select(self):
        """
        Select the item and generate a new menu.
        """
        all = []
        for start, stop in self.query[0]:
            result = yield self._query(start, stop, limit=1)
            if len(result) == 1:
                all.append((start[self.query[1]], result[0]))
        items = self.get_items(all)
        if isinstance(items, kaa.InProgress):
            items = yield items
        menu = freevo.Menu(self.name, items, type='image')
        menu.autoselect = True
        self.menustack.pushmenu(menu)


class MonthItem(BeaconQueryItem):
    """
    Item for one month.
    """
    def __init__(self, year, month, sample, parent):
        name = _('%s-%s') % (year, month)
        BeaconQueryItem.__init__(self, name, parent, sample)
        self.query = [ ((year, month, x), (year, month, x)) for x in range(1, 32) ], 2
        self._year = year
        self._month = month

    @kaa.coroutine()
    def get_items(self, result):
        """
        Return days as Playlist items
        """
        items = []
        for day, sample in result:
            result = yield self._query((self._year, self._month, day), (self._year, self._month, day))
            p = freevo.Playlist(_('%s-%s-%s') % (self._year, self._month, day), playlist=result, parent=self, type='image')
            p.info['thumbnail'] = result[0].get('thumbnail')
            items.append(p)
        yield items


class YearItem(BeaconQueryItem):
    """
    Item for one year.
    """
    def __init__(self, year, sample, parent):
        BeaconQueryItem.__init__(self, unicode(year), parent, sample)
        self.query = [ ((year, x, 1), (year, x, 31)) for x in range(1, 13) ], 1
        self._year = year

    def get_items(self, result):
        """
        Return months as MonthItem items.
        """
        return [ MonthItem(self._year, month, sample, self) for month, sample in result ]


class CalendarItem(BeaconQueryItem):
    """
    Item for the whole calendar.
    """
    def __init__(self, parent):
        BeaconQueryItem.__init__(self, _('Calendar'), parent)
        self.query = [ ((x, 1, 1), (x,12,31)) for x in range(1970, 2037) ], 0

    def get_items(self, result):
        """
        Return years as YearItem items.
        """
        return [ YearItem(year, sample, self) for year, sample in result ]


class PluginInterface(freevo.MainMenuPlugin):
    """
    Calendar view plugin.
    """
    plugin_media = 'image'

    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ CalendarItem(parent) ]
