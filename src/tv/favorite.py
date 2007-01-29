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

# freevo core imports
import freevo.ipc

# freevo imports
from freevo.ui.menu import Item, Action, Menu
from application import MessageWindow

# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver

class FavoriteItem(Item):
    """
    A favorite item to add/delete/change a favorite for the recordserver.
    """
    def __init__(self, name, start, parent):
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
        return [ Action(_('Add as favorite'), self.add) ]


    def submenu(self):
        """
        show a submenu for this item
        """
        items = []
        for action in self.actions():
            items.append(Item(self, action))
        s = Menu(self, items, type = 'tv favorite menu')
        s.submenu = True
        s.infoitem = self
        self.pushmenu(s)


    def add(self):
        tvserver.favorites.add(self)
        txt = _('"%s" has been scheduled as favorite') % self.title
        MessageWindow(txt).show()
