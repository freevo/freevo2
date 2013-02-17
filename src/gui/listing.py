# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Listing widgets
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2009-2013 Dirk Meyer, et al.
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

__all__ = [ 'AbstractListing', 'Listing', 'FixedSelectionListing', 'GridListing' ]

# python imports
import logging

# kaa imports
import kaa

# gui imports
import kaa.candy

# get logging object
log = logging.getLogger('gui')

kaa.candy.Eventhandler.signatures['listing-select'] = 'prev,next,secs'

class AbstractListing(kaa.candy.SelectionGrid):
    candyxml_name = 'listing'
    candyxml_style = 'abstract'

    __previous_selected = None

    def __init__(self, pos, size, template, selection, xpadding=None, ypadding=None, menu=None, context=None):
        self.__menu = menu or 'menu'
        menu = context.get(self.__menu)
        super(AbstractListing, self).__init__(pos, size, None, 'item', menu.choices,
            template, selection, kaa.candy.SelectionGrid.VERTICAL, xpadding, ypadding, context)
        self.selected = menu.selected
        # store the position of the menu in the stack. For listings
        # not based on menus (e.g. on a playlist) pos is always 0
        # because this kind of objects have no pos attribute
        self.pos = getattr(menu, 'pos', None)
        self.state = menu.state
        # A new menu means we want to be exchanged with a new version
        # of ourself and not reused.
        self.add_dependencies(self.__menu)

    @property
    def menu(self):
        return self.context.get(self.__menu)

    @property
    def example_item(self):
        context = self.context.copy()
        context[self.cell_item] = self.items[0]
        self.template(context=context)
        return self.template(context=context)

    def emit_select(self, pos, secs):
        if not pos in self.item_widgets:
            self.sync_prepare()
        selected = self.item_widgets.get(pos)
        if not selected:
            log.error('unable to get selected item')
        elif self.__previous_selected != selected:
            self.emit('listing-select', self.__previous_selected, selected, secs)
            self.__previous_selected = selected

    def sync_context(self):
        if self.create_grid:
            self.create_grid()
        if self.state != self.menu.state:
            if self.items == self.menu.choices:
                # kaa.candy has no way to redraw items in a grid and
                # clears it when the items list changes. Since the
                # state may only indicate that a text inside the menu
                # changes we have to force a redraw here. This should
                # be fixed in future versions.
                self.clear()
            self.items = self.menu.choices
            self.state = self.menu.state

    def create_grid(self):
        super(AbstractListing, self).create_grid()
        self.menu.cols = self.num_items_x
        self.menu.rows = self.num_items_y

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        return super(AbstractListing, cls).candyxml_parse(element).\
            remove('cell_item', 'cell_size', 'items', 'orientation').\
            update(xpadding=int(element.xpadding or 0), ypadding=int(element.ypadding or 0),
                   menu=element.menu or 'menu')



class Listing(AbstractListing):
    """
    Listing widget to show a menu.
    """
    candyxml_style = None

    __grid_position = 0

    def sync_context(self):
        super(Listing, self).sync_context()
        if self.selected != self.menu.selected:
            self.select((0, self.menu.selected_pos), 0.2)
        self.selected = self.menu.selected

    def clear(self):
        super(Listing, self).clear()
        self.select((0, self.menu.selected_pos), 0)

    def select(self, pos, secs):
        super(Listing, self).select(pos, secs)
        if self.menu.selected_pos / self.num_items_y != self.__grid_position:
            self.__grid_position = self.menu.selected_pos / self.num_items_y
            self.scroll_to((0, self.__grid_position * self.num_items_y), secs)
        self.emit_select(pos, secs)

    def create_grid(self):
        context = self.context.copy()
        context[self.cell_item] = self.items[0]
        self.cell_size = self.width - self.item_padding[0], self.template(context=context).height
        super(Listing, self).create_grid()
        self.select((0, self.menu.selected_pos), 0)


class FixedSelectionListing(AbstractListing):

    candyxml_style = 'fixed-selection'

    def __init__(self, pos, size, template, selection, selection_pos=2, xpadding=0, ypadding=0, menu=None, context=None):
        super(FixedSelectionListing, self).__init__(pos, size, template, selection, xpadding, ypadding, menu, context)
        self.selection_pos = selection_pos

    def sync_context(self):
        super(FixedSelectionListing, self).sync_context()
        if self.selected != self.menu.selected:
            self.select(self.menu.selected_pos, 0.2)
        self.selected = self.menu.selected

    def create_grid(self):
        self.cell_size = None
        item_width, item_height = self.example_item.size
        if item_width > 0 and item_height > 0:
            self.cell_size = item_width, item_height
        item_width = item_width if item_width > 0 else self.width
        item_height = item_height if item_height > 0 else self.height
        if self.width / (item_width + self.item_padding[0]) > 1 and \
                self.height / (item_height + self.item_padding[1]) == 1:
            self.orientation = 'horizonal'
            if not self.cell_size:
                self.cell_size = self.item.width, self.height - self.item_padding[1]
        else:
            self.orientation = 'vertical'
            if not self.cell_size:
                self.cell_size = self.width - self.item_padding[0], self.example_item.height
        super(FixedSelectionListing, self).create_grid()
        self.selection.parent = self
        self.selection.lower_bottom()
        if self.orientation == 'vertical':
            self.selection.x += self.item_group.x
            self.selection.y += self.item_group.y + self.selection_pos * self.item_height
        else:
            self.selection.x += self.item_group.x + self.selection_pos * self.item_width
            self.selection.y += self.item_group.y
        self.select(self.menu.selected_pos, 0)

    def clear(self):
        super(FixedSelectionListing, self).clear()
        self.selection.parent = self
        self.selection.lower_bottom()
        self.select(self.menu.selected_pos, 0)

    def select(self, pos, secs):
        if self.orientation == 'vertical':
            self.scroll_to((0, pos - self.selection_pos), secs)
            self.emit_select((0, pos), secs)
        else:
            self.scroll_to((pos - self.selection_pos, 0), secs)
            self.emit_select((pos, 0), secs)

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        return super(FixedSelectionListing, cls).candyxml_parse(element).update(
            selection_pos=int(element.selection or 2))


class GridListing(AbstractListing):
    """
    Listing widget to show a menu.
    """
    candyxml_style = 'grid'
    __grid_position = 0

    def create_grid(self):
        self.cell_size = self.example_item.size
        super(GridListing, self).create_grid()
        pos = self.menu.selected_pos
        self.select((pos % self.num_items_x, pos / self.num_items_x), 0)

    def clear(self):
        super(GridListing, self).clear()
        pos = self.menu.selected_pos
        self.select((pos % self.num_items_x, pos / self.num_items_y), 0)

    def select(self, pos, secs):
        super(GridListing, self).select(pos, secs)
        if self.__grid_position != self.menu.selected_pos / (self.num_items_x * self.num_items_y):
            self.__grid_position = self.menu.selected_pos / (self.num_items_x * self.num_items_y)
            self.scroll_to((0, self.__grid_position * self.num_items_y), secs)
        self.emit_select(pos, secs)

    def sync_context(self):
        super(GridListing, self).sync_context()
        if self.selected != self.menu.selected:
            self.select((self.menu.selected_pos % self.num_items_x, self.menu.selected_pos / self.num_items_x), 0.2)
        self.selected = self.menu.selected
