# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# favorite.py -
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rob@infointeractive.com>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#                Rob Shortt <rob@infointeractive.com>
#
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
# -----------------------------------------------------------------------------

# freevo imports
import menu
from item import Item
from gui import AlertBox

# tv imports
import record.client


class FavoriteItem(Item):
    """
    A favorite item to add/delete/change a favorite for the recordserver.
    """
    def __init__(self, name, start, parent=None):
        Item.__init__(self, parent)
        self.name  = self.title = name
        self.start = start

        # FIXME: create correct informations here
        self.channel = 'ANY'
        self.days    = 'ANY'
        self.time    = 'ANY'


    def __getitem__(self, key):
        """
        return the specific attribute as string or an empty string
        """
        if key == 'date':
            return self.days
        if key == 'channel':
            if self.channel == 'ANY':
                return self.channel
            return self.channel.name
        return Item.__getitem__(self, key)


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        return [ (self.add, _('Add as favorite')) ]


    def submenu(self, arg=None, menuw=None):
        """
        show a submenu for this item
        """
        items = []
        for function, title in self.actions():
            items.append(menu.MenuItem(title, function))
        s = menu.Menu(self, items, item_types = 'tv favorite menu')
        s.is_submenu = True
        s.infoitem = self
        menuw.pushmenu(s)


    def add(self, arg=None, menuw=None):
        (result, msg) = record.client.favorites.add(self)
        if result:
            AlertBox(text=_('"%s" has been scheduled as favorite') % \
                     self.title).show()
        else:
            AlertBox(text=_('Scheduling Failed')+(': %s' % msg)).show()
