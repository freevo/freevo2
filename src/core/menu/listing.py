# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# listing.py - a simple item listing
# -----------------------------------------------------------------------------
# $Id$
#
# The file holds the base class for an item listing. It is used for the
# Menu and for Playlist items. One base class makes it possible to share
# some code between the two classes and a future gui widget for kaa.candy
# can be created to draw both.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2011 Dirk Meyer, et al.
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

__all__ = [ 'ItemList' ]

# python imports
import logging

# menu imports
from item import Item

# get logging object
log = logging.getLogger()

class ItemList(object):
    """
    A basic listing of items.
    """
    def __init__(self, choices=None, selected=None):
        # state, will increase on every item change
        self.state = 0
        # set items
        self.choices = []
        self.selected = None
        self.selected_id = None
        self.selected_pos = -1
        if choices is not None:
            self.set_items(choices, selected)

    def set_items(self, items, selected=None):
        """
        Set/replace the items.
        """
        # increase state variable
        self.state += 1
        # set new choices and selection
        self.choices = items
        # select given item
        if selected is not None:
            return self.select(selected)
        # try to reset selection in case we had one
        if not self.selected:
            # no old selection
            if len(self.choices):
                return self.select(self.choices[0])
            return self.select(None)
        if self.selected in self.choices:
            # item is still there, reuse it
            return self.select(self.selected)
        for c in self.choices:
            if c.uid == self.selected_id:
                # item with the same id is there, use it
                return self.select(c)
        if self.choices:
            # item is gone now, try to the selection close
            # to the old item
            pos = max(0, min(self.selected_pos-1, len(self.choices)-1))
            return self.select(self.choices[pos])
        # no item in the list
        return self.select(None)

    def select(self, item):
        """
        Set the selection to a specific item in the list. If item in an int
        select a new item relative to current selected
        """
        if self.selected == item:
            # nothing changed
            return True
        if not self.choices or item is None:
            # We have no choices and can't select. This could happen
            # when a Directory Item has no Items
            self.selected = None
            self.selected_pos = -1
            return True
        if isinstance(item, Item):
            # select item
            if not item in self.choices:
                log.error('%s not in list', item)
                ItemList.select(self, self.choices[0])
                return False
            self.selected = item
            self.selected_pos = self.choices.index(item)
            self.selected_id  = self.selected.uid
            return True
        # select relative
        p = min(max(0, self.selected_pos + item), len(self.choices) - 1)
        return ItemList.select(self, self.choices[p])

    def get_items(self):
        """
        Return the list of items.
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
