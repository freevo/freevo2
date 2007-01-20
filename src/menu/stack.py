# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# stack.py - Menu stack for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a menu stack. It is not connected to the GUI so the real
# menu widget must inherit from this class and override the basic GUI functions
# show, hide and redraw.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First edition: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
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

__all__ = [ 'MenuStack' ]

# python imports
import logging

# kaa imports
from kaa.weakref import weakref

# freevo imports
from event import *

# menu imports
from menu import Menu
from item import Item

# get logging object
log = logging.getLogger('menu')


class MenuStack(object):
    """
    The MenuStack handles a stack of Menus
    """
    def __init__(self):
        self.menustack = []


    def back_to_menu(self, menu, refresh=True):
        """
        Go back to the given menu.
        """
        while len(self.menustack) > 1 and self.menustack[-1] != menu:
            self.menustack.pop()
        if refresh:
            self.refresh(True)


    def back_one_menu(self, refresh=True):
        """
        Go back one menu page.
        """
        if len(self.menustack) == 1:
            return
        self.menustack.pop()
        if refresh:
            self.refresh(True)


    def delete_submenu(self, refresh=True, reload=False, osd_message=''):
        """
        Delete the last menu if it is a submenu. Also refresh or reload the
        new menu if the attributes are set to True. If osd_message is set,
        this message will be send if the current menu is no submenu
        """
        if len(self.menustack) > 1 and self.menustack[-1].submenu:
            self.back_one_menu(refresh)
        elif len(self.menustack) > 1 and osd_message:
            OSD_MESSAGE.post(osd_message)


    def pushmenu(self, menu):
        """
        Add a new Menu to the stack and show it
        """
        # set stack (self) pointer to menu
        menu.stack = weakref(self)

        if len(self.menustack) > 0:
            previous = self.menustack[-1]
        else:
            previous = None

        # set menu.pos and append
        menu.pos = len(self.menustack)
        self.menustack.append(menu)

        if menu.autoselect and len(menu.choices) == 1:
            log.info('autoselect action')
            # autoselect only item in the menu
            menu.choices[0].get_actions()[0]()
            return

        # refresh will do the update
        self.refresh()


    def refresh(self, reload=False):
        """
        Refresh the stack and redraw it.
        """
        menu = self.menustack[-1]

        if menu.autoselect and len(menu.choices) == 1:
            # do not show a menu with only one item. Go back to
            # the previous page
            log.info('delete menu with only one item')
            return self.back_one_menu()

        if reload and menu.reload_func:
            # The menu has a reload function. Call it to rebuild
            # this menu. If the functions returns something, replace
            # the old menu with the returned one.
            new_menu = menu.reload_func()
            if new_menu:
                self.menustack[-1] = new_menu
                menu = new_menu

        return


    def __getitem__(self, attr):
        """
        Return menustack item.
        """
        return self.menustack[attr]


    def __setitem__(self, attr, value):
        """
        Set menustack item.
        """
        self.menustack[attr] = value


    def get_selected(self):
        """
        Return the current selected item in the current menu.
        """
        return self.menustack[-1].selected


    def get_menu(self):
        """
        Return the current menu.
        """
        return self.menustack[-1]


    def eventhandler(self, event):
        """
        Eventhandler for menu control
        """
        menu = self.menustack[-1]

        if menu.eventhandler(event):
            self.refresh()
            return True

        if event == MENU_GOTO_MAINMENU:
            while len(self.menustack) > 1:
                menu = self.menustack.pop()
            self.refresh()
            return True

        if event == MENU_BACK_ONE_MENU:
            self.back_one_menu()
            return True

        if event == MENU_GOTO_MEDIA:
            # TODO: it would be nice to remember the current menu stack
            # but that is something we have to do inside mediamenu if it
            # is possible at all.
            # FIXME: using display_type here is ugly
            if len(self.menustack) > 1 and \
                   hasattr(self.menustack[0].selected, 'display_type') and \
                   self.menustack[0].selected.display_type == event.arg:
                # already in that menu
                return True
            menu = self.menustack[0]
            for item in menu.choices:
                if hasattr(item, 'display_type') and \
                       item.display_type == event.arg:
                    self.menustack = [ menu ]
                    menu.select(item)
                    item.actions()[0]()
                    return True
            return True

        # handle empty menus
        if not menu.choices:
            if event in ( MENU_SELECT, MENU_SUBMENU, MENU_PLAY_ITEM):
                self.back_one_menu()
                return True
            selected = getattr(self.menustack[-2], 'selected', None)
            if selected and selected.eventhandler(event):
                return True
            return False

        if menu.selected and menu.selected.eventhandler(event):
            return True

        return False
