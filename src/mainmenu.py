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
# Copyright (C) 2005-2008 Dirk Meyer, et al.
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

# freevo imports
from freevo import plugin
import api as freevo


class MainMenuItem(freevo.Item):
    """
    This class is a main menu item. Items of this type can be returned by
    a MainMenuPlugin.
    """
    def __init__( self, parent=None, name=None, type=None, image=None):
        super(MainMenuItem, self).__init__(parent)
        if name:
            self.name = name
        # FIXME: add a relative path to the image/watermark
        # of the item with the full path in the candy image path
        self.image = image
        self.type = type
        if not type and not parent.parent:
            # this is the first page, force type to 'main'
            self.type = 'main'

    def get_submenu(self):
        """
        Return submenu items.
        """
        items = super(MainMenuItem, self).get_submenu()
        for i in items:
            i.image = None
        return items


class MainMenuPlugin(plugin.Plugin):
    """
    Plugin class for plugins to add something to the main menu
    """
    def items(self, parent):
        """
        Return the list of items for the main menu
        """
        return []

    @staticmethod
    def plugins(subtype=None):
        """
        Return all MainMenuPlugins.
        """
        return [ x for x in MainMenuPlugin.plugin_list if x.plugin_media() == subtype ]


class MenuWidget(freevo.Application, freevo.MenuStack):
    """
    The MenuWidget is an Application for GUI and event handling and also
    an instance of MenuStack defined in menu.stack.
    """

    name = 'menu'

    def __init__(self, menu):
        freevo.Application.__init__(self, 'menu', (freevo.CAPABILITY_TOGGLE,))
        freevo.MenuStack.__init__(self)
        self.pushmenu(menu)
        self.status = freevo.STATUS_RUNNING
        self.signals['show'].connect_weak(self.refresh, True)


    def refresh(self, reload=False):
        if self.is_locked():
            return
        freevo.MenuStack.refresh(self, reload)
        if self.gui_context.menu != self.menustack[-1]:
            self.gui_context.previous = self.gui_context.menu
            self.gui_context.next = self.menustack[-1]
            self.gui_context.menu = self.menustack[-1]
            self.gui_context.type = self.menustack[-1].type
        self.gui_context.item = self.menustack[-1].selected.properties

    def eventhandler(self, event):
        """
        Eventhandler for menu control
        """
        return freevo.MenuStack.eventhandler(self, event)


class MainMenu(freevo.Item):
    """
    This class handles the main menu. It will start the main menu widget
    and the first menu page based on the main menu plugins.
    """
    def __init__(self):
        """
        Setup the main menu and handle events (remote control, etc)
        """
        super(MainMenu, self).__init__(None)
        items = []
        for p in MainMenuPlugin.plugins():
            items += p.items(self)
        menu = freevo.Menu(_('Freevo Main Menu'), items, type='main')
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
