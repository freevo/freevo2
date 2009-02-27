# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# gridmenu.py - a page for the gridmenu stack
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2009 Dirk Meyer, et al.
#
# First Edition: Joost <joost.kop@gmail.com>
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

__all__ = [ 'GridMenu' ]

# python imports
import logging

# kaa imports
from kaa.weakref import weakref

# freevo imports
from .. import api as freevo

# menu imports
from item import Item
from menu import Menu

# get logging object
log = logging.getLogger()

class GridMenu(Menu):
    """
    A Menu page with Items in grid form for the MenuStack.
    It is not allowed to change the selected item or the
    internal selection directly, use 'select' or 'set_items'
    to do this.
    The grid is drawn row by row. The advanced_mode of this
    menu allowes row items to have different width.
    """
    next_id = 0

    def __init__( self, heading, grid = None, reload_func = None, type = None ):
        Menu.__init__(self, heading, reload_func = reload_func, type=type)
        # Defines if the advanced mode is used
        self.advanced_mode = False

        # set items
        self.selected_col = 0
        self.selected_row = 0
        self.base_col = 0
        self.base_row = 0
        self.last_base_col = -1
        self.last_base_row = -1
        self.update_view = True
        self.set_items(grid, refresh=False)


    def set_items(self, grid=None, selected=None, refresh=True):
        """
        Set/replace the items.
        """
        if grid is None:
            grid = []

        # delete ref to menu for old items
        for c in self.choices:
            for r in c:
                if self.advanced_mode:
                    r[1].menu = None
                else:
                    r.menu = None
        # increase state variable
        self.state += 1

        # set new items and selection
        self.choices = grid

        # select given item
        if selected is not None:
            self.select(selected)

        # try to reset selection in case we had one
        if not self.selected:
            # no old selection
            if len(self.choices):
                 self.select(col=0, row=0)

        # set menu (self) pointer to the items
        sref = weakref(self)
        for c in self.choices:
            for r in c:
                # Check if advanced mode is used
                if self.advanced_mode:
                    r[1].menu = sref
                else:
                    r.menu = sref

        if refresh and self.stack:
            self.stack.refresh()


    def select(self, item=None, col=0, row=0, refresh=True):
        """
        Set the selection to a specific item in the list. If item in an int
        select a new item relative to current selected
        """
        if isinstance(item, Item):
            # select item
            for pos, row in enumerate(self.choices):
                row_items = row
                if self.advanced_mode:
                    row_items = [ i[1] for i in row ]
                if item in row_items:
                    self.selected_col = row_items.index(item)
                    self.selected_row = pos
                    self.selected = item
                    break
            else:
                log.error('%s not in list', item)
                return False

        elif item is None:
            # select relative
            self.selected_row = min(max(row, 0), len(self.choices)-1 )
            self.selected_col = min(max(col, 0), len(self.choices[self.selected_row])-1 )
            if self.advanced_mode:
                self.selected = self.choices[self.selected_row][self.selected_col][1]
            else:
                self.selected = self.choices[self.selected_row][self.selected_col]

        self.selected_id  = self.selected.get_id()

        # Find Which columns/rows to draw, the next update
        if self.selected_col-self.base_col > self.cols-1:
            self.base_col = self.selected_col - (self.cols-1)
        elif self.selected_col-self.base_col < 0:
            self.base_col = self.selected_col

        if self.selected_row-self.base_row > self.rows-1:
            self.base_row = self.selected_row - (self.rows-1)
        elif self.selected_row-self.base_row < 0:
            self.base_row = self.selected_row

        # refresh view?
        if (self.last_base_col != self.base_col) or \
           (self.last_base_row != self.base_row):
            self.update_view = True

        return True


    def get_item(self, row, col):
        """
        Return the data for that col, row.
        """
        try:
            return self.choices[self.base_row+row][self.base_col+col]
        except (IndexError, KeyError):
            return None

    def get_item_state(self, row, col):
        """
        Return the state for this item.
        """
        if self.advanced_mode:
            if self.selected == self.get_item(row, col)[1]:
                return 'selected'
            else:
                return 'default'
        else:
            if self.selected == self.get_item(row, col):
                return 'selected'
            else:
                return 'default'


    def get_column_name(self, col):
        """
        Return the column name
        """
        return _("Column %s") % (self.base_col+col)


    def get_row_name(self, row):
        """
        Return the row name
        """
        return _("Row %s") % (self.base_row+row)


    def eventhandler(self, event):
        """
        Handle events for this menu page.
        """
        if self.choices == None:
            return False

        if event == freevo.MENU_UP:
            self.select(col=self.selected_col, row=self.selected_row-1 )
            return True

        if event == freevo.MENU_DOWN:
            self.select(col=self.selected_col, row=self.selected_row+1 )
            return True

        if event == freevo.MENU_PAGEUP:
            self.select(col=self.selected_col, row=self.selected_row-self.rows )
            return True

        if event == freevo.MENU_PAGEDOWN:
            self.select(col=self.selected_col, row=self.selected_row+self.rows )
            return True

        if event == freevo.MENU_LEFT:
            self.select(col=self.selected_col-1, row=self.selected_row )
            return True

        if event == freevo.MENU_RIGHT:
            self.select(col=self.selected_col+1, row=self.selected_row )
            return True

        if event in (freevo.MENU_PLAY_ITEM, freevo.MENU_CHANGE_SELECTION, freevo.MENU_SELECT,
                     freevo.MENU_PLAY_ITEM, freevo.MENU_SUBMENU, freevo.MENU_CALL_ITEM_ACTION):
            return Menu.eventhandler(self, event)

        return False
