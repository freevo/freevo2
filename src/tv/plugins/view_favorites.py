#if 0 /*
# -----------------------------------------------------------------------
# view_favorites.py - A plugin to view your list of favorites. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/03/13 03:28:06  rshortt
# More favorites support... almost there!
#
# Revision 1.1  2004/02/24 04:40:16  rshortt
# Make 'View Favorites' a menu based plugin, still incomplete.
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import os
import config, plugin, menu, rc
import tv.record_client as record_client

from item import Item
from tv.program_display import FavoriteItem
from gui.AlertBox import AlertBox


class ViewFavoritesItem(Item):
    def __init__(self, parent):
        Item.__init__(self, parent, skin_type='tv')
        self.name = _('View Favorites')


    def actions(self):
        return [ ( self.view_favorites , _('View Favorites') ) ]


    def view_favorites(self, arg=None, menuw=None):
        items = []

        (server_available, msg) = record_client.connectionTest()
        if not server_available:
            AlertBox(_('Recording server is unavailable.')+(': %s' % msg),
                     self, Align.CENTER).show()
            return

        (result, favorites) = record_client.getFavorites()
        if result:
            f = lambda a, b: cmp(a.priority, b.priority)
            favorites = favorites.values()
            favorites.sort(f)
            for fav in favorites:
                print 'FAV: name=%s mod=%s' % (fav.name, fav.mod)
                items.append(FavoriteItem(self, fav))

        else:
            AlertBox(_('Get favorites failed')+(': %s' % favorites),
                     self, Align.CENTER).show()
            return

        favorite_menu = menu.Menu(_( 'View Favorites'), items,
                                  item_types = 'tv favorite menu')
        rc.app(None)
        menuw.pushmenu(favorite_menu)
        menuw.refresh()


class PluginInterface(plugin.MainMenuPlugin):
    """
    This plugin is used to display your list of favorites.

    plugin.activate('tv.view_favorites')

    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)

    def items(self, parent):
            return [ ViewFavoritesItem(parent) ]


