# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# menu.py - a page for the menu stack
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2011 Dirk Meyer, et al.
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

__all__ = [ 'Menu' ]

# python imports
import logging

# kaa imports
from kaa.weakref import weakref

# freevo imports
from .. import api as freevo

# menu imports
from listing import ItemList
from item import ActionItem

# get logging object
log = logging.getLogger()

def show_config_menu(item):
    """
    Show the item configure submenu
    """
    items = item.cfgitems
    if not len(items):
        # no submenu
        return False
    item.menustack.pushmenu(Menu(_('Configure'), items, type='submenu'))
        

class Menu(ItemList):
    """
    A Menu page with Items for the MenuStack. It is not allowed to
    change the selected item or the internal choices directly, use
    'select', 'set_items' or 'change_item' to do this.
    """
    next_id = 0

    def __init__(self, heading, choices=None, reload_func = None, type = None):
        ItemList.__init__(self, choices)
        self.heading = heading
        self.stack   = None
        # unique id of the menu object
        Menu.next_id += 1
        self.id = Menu.next_id
        # position in the menu stack
        self.pos = -1
        # special items for the new skin to use in the view or info
        # area. If None, menu.selected will be taken
        self.infoitem = None
        # Called when a child menu returns. This function returns a new menu
        # or None and the old menu will be reused
        self.reload_func = reload_func
        self.type = type
        # Autoselect menu if it has only one item
        self.autoselect = False
        # how many rows and cols does the menu has
        # (will be changed by the skin code)
        self.cols = 1
        self.rows = 1

    def set_items(self, items, refresh=True):
        """
        Set/replace the items in this menu. If refresh is True, the menu
        stack will be refreshed and redrawn.
        """
        # delete ref to menu for old choices
        for c in self.choices:
            c.menu = None
        # set new choices and selection
        ItemList.set_items(self, items)
        # set menu (self) pointer to the items
        sref = weakref(self)
        for c in self.choices:
            c.menu = sref
        if refresh and self.stack:
            self.stack.refresh()

    def change_item(self, old, new):
        """
        Replace the item 'old' with the 'new'.
        """
        ItemList.change_item(self, old, new)
        old.menu = None
        new.menu = weakref(self)

    def eventhandler(self, event):
        """
        Handle events for this menu page.
        """
        if not self.choices:
            return False
        if self.cols == 1:
            if freevo.config.menu.arrow_navigation:
                if event == freevo.MENU_LEFT:
                    # event = freevo.MENU_BACK_ONE_MENU
                    # we can not just change the event here because
                    # stack.py processes this.
                    self.stack.back_one_menu()
                elif event == freevo.MENU_RIGHT:
                    event = freevo.MENU_SELECT
            else:
                if event == freevo.MENU_LEFT:
                    event = freevo.MENU_PAGEUP
                elif event == freevo.MENU_RIGHT:
                    event = freevo.MENU_PAGEDOWN
        if event == freevo.MENU_UP:
            self.select(-self.cols)
            return True
        if event == freevo.MENU_DOWN:
            self.select(self.cols)
            return True
        if event == freevo.MENU_PAGEUP:
            self.select(-(self.rows * self.cols))
            return True
        if event == freevo.MENU_PAGEDOWN:
            self.select(self.rows * self.cols)
            return True
        if event == freevo.MENU_LEFT:
            self.select(-1)
            return True
        if event == freevo.MENU_RIGHT:
            self.select(1)
            return True
        if event == freevo.MENU_PLAY_ITEM and hasattr(self.selected, 'play'):
            self.selected.play()
            return True
        if event == freevo.MENU_CHANGE_SELECTION:
            self.select(event.arg)
            return True
        if event == freevo.MENU_SELECT or event == freevo.MENU_PLAY_ITEM:
            actions = self.selected._get_actions()
            if not actions:
                freevo.OSD_MESSAGE.post(_('No action defined for this choice!'))
            else:
                result = actions[0]()
                if result:
                    # action handed this event and returned either True or
                    # an InProgress object
                    return result
            # in any case, return True because this event is handled here
            return True
        if event == freevo.MENU_SUBMENU:
            if self.type == 'submenu' or not self.stack:
                return False
            items = self.selected.subitems
            if self.selected.cfgitems:
                items.append(ActionItem(_('Configure'), self.selected, show_config_menu))
            if len(items) < 2:
                # no submenu
                return False
            self.stack.pushmenu(Menu(self.selected.name, items, type='submenu'))
            return True
        if event == freevo.MENU_CALL_ITEM_ACTION:
            log.info('calling action %s' % event.arg)
            for action in self.selected._get_actions():
                if action.shortcut == event.arg:
                    return action() or True
            log.info('action %s not found' % event.arg)
            return True
        return False
