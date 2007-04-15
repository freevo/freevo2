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

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

DAY_NAMES = (_('Sun'), _('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'))

class FavoriteItem(Item):
    """
    A favorite item to add/delete/change a favorite for the recordserver.
    """

    def __init__(self, parent, fav):
        Item.__init__(self, parent)

        self.new = True
        self.id = 0
        if isinstance(fav, kaa.epg.Program):
            # created with Program object
            # Convert to 0=Sunday - 6=Saterday
            day = min(time.localtime(fav.start)[6] + 1, 6)
            self.days = [ day ]
            self.name = self.title = fav.title
            self.channels = [ fav.channel.name ]
            #check if already a favorite
            for f in tvserver.favorites.list():
                if fav.title == f.title:
                    if fav.channel.name in f.channels:
                        if day in f.days:
                            self.new = False
                            self.id = f.id
        else:
            # created with ipc Favorite object
            self.name = self.title = fav.title
            self.days = fav.days
            self.channels = fav.channels
            self.new = False
            self.id = fav.id


    def __getitem__(self, key):
        """
        return the specific attribute as string or an empty string
        """
        if key == 'date':
            if self.days == 'ANY':
                return 'ANY'
            else:
                days = ', '.join(['%s' % DAY_NAMES[d] for d in self.days])
                return days
        if key == 'channel':
            if self.channels == 'ANY':
                return 'ANY'
            else:
                channels = ', '.join(['%s' % chan for chan in self.channels])
                return channels
        return Item.__getitem__(self, key)


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
        
        s = Menu(self, items, type = 'tv favorite menu')
        s.submenu = True
        s.infoitem = self
        self.pushmenu(s)


    @kaa.notifier.yield_execution()
    def add(self):
        result = tvserver.favorites.add(self.title, self.channels, self.days,
                                        'ANY', 50, False)
        if isinstance(result, kaa.notifier.InProgress):
            yield result
            result = result()
        if result != tvserver.favorites.SUCCESS:
            text = _('Adding favorite Failed')+(': %s' % result)
        else:
            text = _('"%s" has been scheduled as favorite') % self.title
        MessageWindow(text).show()
        self.get_menustack().delete_submenu()


    @kaa.notifier.yield_execution()
    def remove(self):
        result = tvserver.favorites.remove(self.id)
        if isinstance(result, kaa.notifier.InProgress):
            yield result
            result = result()
        if result != tvserver.favorites.SUCCESS:
            text = _('Remove favorite Failed')+(': %s' % result)
            MessageWindow(text).show()
        self.get_menustack().delete_submenu()
