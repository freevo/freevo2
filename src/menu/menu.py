# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# menu.py - a page for the menu stack
# -----------------------------------------------------------------------------
# $Id$
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

__all__ = [ 'Menu' ]

# python imports
import gc
import logging

# kaa imports
from kaa.weakref import weakref

# freevo imports
import config
from event import *

# menu imports
from item import Item

# get logging object
log = logging.getLogger()

class Menu(object):
    """
    A Menu page with Items for the MenuStack. It is not allowed to change
    the selected item or the internal choices directly, use 'select',
    'set_items' or 'change_item' to do this.
    """
    next_id = 0

    def __init__(self, heading, choices=[], reload_func = None, type = None):

        self.heading = heading
        self.stack   = None

        # unique id of the menu object
        Menu.next_id += 1
        self.id = Menu.next_id
        # state, will increase on every item change
        self.state = 0
        # position in the menu stack
        self.pos = -1

        # set items
        self.choices = []
        self.selected = None
        self.set_items(choices, False)

        # special items for the new skin to use in the view or info
        # area. If None, menu.selected will be taken
        self.infoitem = None
        self.viewitem = None

        # Called when a child menu returns. This function returns a new menu
        # or None and the old menu will be reused
        self.reload_func = reload_func
        self.type = type

        # Menu type
        self.submenu = False

        # Reference to the item that created this menu
        self.item = None

        # Autoselect menu if it has only one item
        self.autoselect = False

        # If the menu is the current visible and the menu stack itself is
        # visible, this variable is True
        self.visible= False

        # how many rows and cols does the menu has
        # (will be changed by the skin code)
        self.cols = 1
        self.rows = 1


    def show(self):
        """
        Show the menu. This will be called when this menu is on top of the
        menu stack.
        """
        self.visible = True


    def hide(self):
        """
        Hide the menu. A different menu is on top or the stack itself is not
        visible.
        """
        self.visible = False


    def set_items(self, items, refresh=True):
        """
        Set/replace the items in this menu. If refresh is True, the menu
        stack will be refreshed and redrawn.
        """
        # increase state variable
        self.state += 1

        # delete ref to menu for old choices
        for c in self.choices:
            c.menu = None

        # set new choices and selection
        self.choices = items

        # set menu (self) pointer to the items
        sref = weakref(self)
        for c in self.choices:
            c.menu = sref

        # try to reset selection in case we had one
        if not self.selected:
            # no old selection
            if len(self.choices):
                self.select(self.choices[0])
            else:
                self.select(None)

        elif self.selected in self.choices:
            # item is still there, reuse it
            self.select(self.selected)

        else:
            for c in self.choices:
                if c.__id__() == self.selected_id:
                    # item with the same id is there, use it
                    self.select(c)
                    break
            else:
                if self.choices:
                    # item is gone now, try to the selection close
                    # to the old item
                    pos = max(0, min(self.selected_pos-1, len(self.choices)-1))
                    self.select(self.choices[pos])
                else:
                    # no item in the list
                    self.select(None)

        if refresh and self.stack:
            self.stack.refresh()


    def select(self, item):
        """
        Set the selection to a specific item in the list. If item in an int
        select a new item relative to current selected
        """
        if isinstance(item, Item):
            # select item
            self.selected     = item
            try:
                self.selected_pos = self.choices.index(item)
                self.selected_id  = self.selected.__id__()
            except ValueError, e:
                log.exception('crash by select %s in %s' % (item, self.choices))
                if self.choices:
                    self.select(self.choices[0])
                else:
                    self.select(None)
        elif item == None:
            # nothing to select
            self.selected     = None
            self.selected_pos = -1
        else:
            # select relative
            p = min(max(0, self.selected_pos + item), len(self.choices) - 1)
            self.select(self.choices[p])


    def get_items(self):
        """
        Return the list of items in this menu.
        """
        return self.choices


    def get_selection(self):
        """
        Return current selected item.
        """
        return self.selected


    def change_item(self, old, new):
        """
        Replace the item 'old' with the 'new'.
        """
        # increase state variable
        self.state += 1

        # change item
        self.choices[self.choices.index(old)] = new
        if self.selected == old:
            self.select(new)
        old.menu = None
        new.menu = weakref(self)


    def eventhandler(self, event):
        """
        Handle events for this menu page.
        """

        if not self.choices:
            return False

        if self.cols == 1:
            if config.MENU_ARROW_NAVIGATION:
                if event == MENU_LEFT:
                    event = MENU_BACK_ONE_MENU
                elif event == MENU_RIGHT:
                    event = MENU_SELECT
            else:
                if event == MENU_LEFT:
                    event = MENU_PAGEUP
                elif event == MENU_RIGHT:
                    event = MENU_PAGEDOWN

        if self.rows == 1:
            if event == MENU_LEFT:
                event = MENU_UP
            if event == MENU_RIGHT:
                event = MENU_DOWN

        if event == MENU_UP:
            self.select(-self.cols)
            return True

        if event == MENU_DOWN:
            self.select(self.cols)
            return True

        if event == MENU_PAGEUP:
            self.select(-(self.rows * self.cols))
            return True

        if event == MENU_PAGEDOWN:
            self.select(self.rows * self.cols)
            return True

        if event == MENU_LEFT:
            self.select(-1)
            return True

        if event == MENU_RIGHT:
            self.select(1)
            return True

        if event == MENU_PLAY_ITEM and hasattr(self.selected, 'play'):
            self.selected.play()
            return True

        if event == MENU_CHANGE_SELECTION:
            self.select(event.arg)
            return True

        if event == MENU_SELECT or event == MENU_PLAY_ITEM:
            actions = self.selected.get_actions()
            if not actions:
                OSD_MESSAGE.post(_('No action defined for this choice!'))
            else:
                actions[0]()
            return True

        if event == MENU_SUBMENU:
            if self.submenu or not self.stack:
                return False

            actions = self.selected.get_actions()
            if not actions or len(actions) <= 1:
                return False
            items = []
            for a in actions:
                items.append(Item(self.selected, a))

            for i in items:
                if not self.selected.type == 'main':
                    i.image = self.selected.image
                if hasattr(self.selected, 'display_type'):
                    i.display_type = self.selected.display_type
                else:
                    i.display_type = self.selected.type

            s = Menu(self.selected.name, items)
            s.submenu = True
            s.item = self.selected
            self.stack.pushmenu(s)
            return True

        if event == MENU_CALL_ITEM_ACTION:
            log.info('calling action %s' % event.arg)
            for action in self.selected.get_actions():
                if action.shortcut == event.arg:
                    action()
                    return True
            log.info('action %s not found' % event.arg)
            return True

        return False


    def __del__(self):
        """
        Delete function of memory debugging
        """
        log.info('Delete menu %s' % self.heading)
