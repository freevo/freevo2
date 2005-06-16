# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# menu.py - a page for the menu stack
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First edition: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'Menu' ]

# python imports
import gc
import logging

# Freevo imports
from util.weakref import weakref

# get logging object
log = logging.getLogger()

class Menu:
    """
    A Menu page with Items for the MenuStack
    """
    def __init__(self, heading, choices=[], theme=None,
                 reload_func = None, item_types = None,
                 force_skin_layout = -1):

        self.heading = heading
        self.choices = choices
        self.stack   = None
        if len(self.choices):
            self.selected = self.choices[0]
            self.selected_pos = 0
        else:
            self.selected = None
            self.selected_pos = -1

        # set menu (self) pointer to the items
        sref = weakref(self)
        for c in choices:
            c.menu = sref

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

        # How many menus to go back when 'BACK_ONE_MENU' is called
        self.back_one_menu = 1

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


    def change_selection(self, rel):
        """
        select a new item relative to current selected
        """
        self.selected_pos = min(max(0, self.selected_pos + rel),
                                len(self.choices) - 1)
        self.selected = self.choices[self.selected_pos]


    def set_selection(self, item):
        """
        set the selection to a specific item in the list
        """
        if item:
            self.selected     = item
            self.selected_pos = self.choices.index(item)
        else:
            self.selected     = None
            self.selected_pos = -1


    def __del__(self):
        """
        delete function of memory debugging
        """
        log.info('Delete menu %s' % self.heading)
        # run gc (for debugging)
        gc.collect()
        # check for more garbage
        g = gc.collect()
        if g:
            log.warning('Garbage: %s' % gc.collect())
            for g in gc.garbage:
                log.warning(' %s' % g)

