# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# favorites.py - A plugin to view your list of favorites. 
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al. 
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
# ----------------------------------------------------------------------- */


from freevo.ui.menu import Item, Menu, ActionItem

from freevo.ui.mainmenu import MainMenuPlugin
from freevo.ui.tv.favorite import FavoriteItem
from freevo.ui.application import MessageWindow

# freevo core imports
import freevo.ipc
# get tvserver interface
tvserver = freevo.ipc.Instance('freevo').tvserver


class PluginInterface(MainMenuPlugin):
    """
    This plugin is used to display your list of favorites.
    """
    def favorites(self, parent):
        """
        Show all favorites.
        """
        self.parent = parent
        items = self.get_items()
        if items:
            self.menu = Menu(_('View Favorites'), items, type='tv favorite menu',
                             reload_func = self.reload_favorites)
            parent.get_menustack().pushmenu(self.menu)
        else:
            MessageWindow(_("You don't have any favorites.")).show()

    def reload_favorites(self):
        items = self.get_items()
        if items:
            self.menu.set_items(items)
        else:
            self.parent.get_menustack().back_one_menu()

    def get_items(self):
        items = []
        fav = tvserver.favorites.list()
        for f in fav:
            items.append(FavoriteItem(self.parent, f))
        return items

    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ ActionItem(_('View Favorites'), parent, self.favorites) ]
