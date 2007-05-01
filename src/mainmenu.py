# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mainmenu.py - Freevo main menu page
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains the main menu and a class for main menu plugins. There
# is also eventhandler support for the main menu showing the skin chooser.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2006 Dirk Meyer, et al.
#
# First edition: Dirk Meyer <dischi@freevo.org>
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


__all__ = [ 'MainMenuItem', 'MainMenu', 'MainMenuPlugin' ]

# python imports
import os

# freevo imports
from freevo import plugin
import gui.theme

from menu import Item, Action, Menu
from application.menuw import MenuWidget


class MainMenuItem(Item):
    """
    This class is a main menu item. Items of this type can be returned by
    a MainMenuPlugin.
    """
    def __init__( self, parent=None, name=u'', type=None, image=None,
                  skin_type=None):

        Item.__init__(self, parent)
        self.name = name
        self.image = image
        self.type = type

        if not type and not parent.parent:
            # this is the first page, force type to 'main'
            self.type = 'main'

        if not skin_type and hasattr(self, 'skin_type'):
            skin_type = self.skin_type
        if not skin_type:
            return

        # load extra informations for the skin fxd file
        theme = gui.theme.get()
        skin_info = theme.mainmenu.items
        if skin_info.has_key(skin_type):
            skin_info  = skin_info[skin_type]
            self.name  = _(skin_info.name)
            self.image = skin_info.image

        imagedir = theme.mainmenu.imagedir
        if not self.image and imagedir:
            # find a nice image based on skin type
            self.image = gui.theme.getimage(os.path.join(imagedir, skin_type))


    def actions(self):
        """
        Actions for this item.
        """
        return [ Action(self.name, self.select) ]


    def select(self):
        """
        Select the item (default action). Need to be overloaded by the
        inherting item or actions() need to be overloaded.
        """
        raise RuntimeError("no action defined for %s", self)
    

class MainMenuPlugin(plugin.Plugin):
    """
    Plugin class for plugins to add something to the main menu
    """
    def items(self, parent):
        """
        return the list of items for the main menu
        """
        return []


    def plugins(subtype=None):
        """
        Static function to return all MainMenuPlugins.
        """
        return [ x for x in MainMenuPlugin.plugin_list if x.plugin_media() == subtype ]

    plugins = staticmethod(plugins)


class MainMenu(Item):
    """
    This class handles the main menu. It will start the main menu widget
    and the first menu page based on the main menu plugins.
    """
    def __init__(self):
        """
        Setup the main menu and handle events (remote control, etc)
        """
        Item.__init__(self)
        items = []
        for p in MainMenuPlugin.plugins():
            items += p.items(self)
        menu = Menu(_('Freevo Main Menu'), items, type='main')
        menu.autoselect = True
        self.menuw = MenuWidget(menu)


    def get_menustack(self):
        """
        Get the menustack. This item needs to override this function
        because it is not bound to a menupage.
        """
        return self.menuw

# register base class
plugin.register(MainMenuPlugin)
