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
from kaa.base import weakref

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
    def __init__(self, heading, choices=[], theme=None,
                 reload_func = None, item_types = None,
                 force_skin_layout = -1):

        self.heading = heading
        self.stack   = None

        # set items
        self.choices = []
        self.selected = None
        self.set_items(choices, False)
        
        # skin theme for this menu
        self.theme = None
        if theme:
            self.theme = theme

        # special items for the new skin to use in the view or info
        # area. If None, menu.selected will be taken
        self.infoitem = None
        self.viewitem = None

        # Called when a child menu returns. This function returns a new menu
        # or None and the old menu will be reused
        self.reload_func       = reload_func
        self.item_types        = item_types
        self.force_skin_layout = force_skin_layout

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
        self.choices[self.choices.index(old)] = new
        if self.selected == old:
            self.select(new)
        old.menu = None
        new.menu = weakref(self)

        
    def __del__(self):
        """
        Delete function of memory debugging
        """
        log.info('Delete menu %s' % self.heading)
