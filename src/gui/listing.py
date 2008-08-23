# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# listing.py - Listing Widget
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008 Dirk Meyer, et al.
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

# kaa imports
import kaa

# gui imports
import kaa.candy

class Listing(kaa.candy.Group):
    """
    Listing widget to show a menu.
    """

    class Selection(object):
        def __init__(self):
            self.widget = None
            self.properties = {}

    candyxml_name = 'listing'
    context_sensitive = True

    def __init__(self, pos, size, label, selection, spacing=0, context=None):
        super(Listing, self).__init__(pos, size, context)
        self.spacing = spacing
        self._template = label
        self._selection = selection
        self.grid = None
        self.page = 0
        self.selected = None

    def _create_children(self):
        """
        Create grid and selection children
        """
        # create one label to get some information we need. This widget
        # is only to get the information, it will never be used
        menu = self.eval_context('menu')
        content = self._template()
        # create bar and set the height
        bar = self._selection.widget
        if kaa.candy.is_template(bar):
            bar = bar()
        bar.height = content.height
        # create grid, the location of the bar is not 100% correct
        # because of baseline is not text_height is not label.height
        w = self.inner_width
        h = (self.inner_height / (content.height + self.spacing)) * \
            (content.height + self.spacing)
        self.grid = kaa.candy.SelectionGrid(None, (w,h), (w, content.height),
              'item', menu.choices, self._template, bar, 1, (0, self.spacing))
        self.grid.parent = self

    def _candy_prepare_render(self):
        """
        Prepare rendering
        """
        if self.grid:
            return super(Listing, self)._candy_prepare_render()
        # create one label to get some information we need. This widget
        # is only to get the information, it will never be used
        menu = self.eval_context('menu')
        content = self._template()
        self._create_children()
        menu.rows = self.grid.num_rows
        menu.cols = self.grid.num_cols
        # now add some animations
        if self._selection.properties.get('color'):
            self.grid.behave('color', content.color,
                self._selection.properties.get('color'))
        if self._selection.properties.get('scale'):
            e = float(self._selection.properties.get('scale'))
            self.grid.behave('scale', content.scale, (e, e))
        if self._selection.properties.get('opacity'):
            e = int(self._selection.properties.get('opacity'))
            self.grid.behave('opacity', content.opacity, e)
        self._set_selected(menu.selected_pos, 0)
        super(Listing, self)._candy_prepare_render()

    def _set_selected(self, idx, secs):
        if not self.grid:
            return
        page = (idx / self.grid.num_rows) * self.grid.num_rows
        if page != self.page:
            self.grid.scroll_to((0, page), secs)
            self.page = page
        self.grid.select((0, idx), secs)

    def set_context(self, context):
        """
        Set a new context for the widget and redraw it.
        """
        super(Listing, self).set_context(context)
        menu = self.get_context('menu')
        if menu.selected == self.selected:
            return
        self.selected = menu.selected
        self._set_selected(menu.selected_pos, 0.3)

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        selection = cls.Selection()
        for child in element:
            if child.node == 'selection':
                for sub in child:
                    if sub.node == 'properties':
                        selection.properties.update(sub.attributes())
                        continue
                    selection.widget = sub.xmlcreate()
                element.remove(child)
                continue
            label = child.xmlcreate()
        return super(Listing, cls).candyxml_parse(element).update(
            label=label, selection=selection, spacing=element.spacing or 0)


class FixedSelectionListing(Listing):

    candyxml_style = 'fixed-selection'

    def _set_selected(self, idx, secs):
        if not self.grid:
            return
        self.grid.scroll_to((0, idx-2), secs)
        self.grid.select((0, idx), secs)


class GridListing(Listing):
    """
    Listing widget to show a menu.
    """
    candyxml_style = 'grid'

    def __init__(self, pos, size, label, selection, spacing=0, context=None):
        super(GridListing,self).__init__(pos, size, label, selection, spacing, context)
        self.viewport = [0,0]
        self._selected_idx = 0
        self._selected_pos = [0,0]

    def _create_children(self):
        """
        Create grid and selection children
        """
        # create one label to get some information we need. This widget
        # is only to get the information, it will never be used
        menu = self.eval_context('menu')
        content = self._template()
        # create bar and set the height
        bar = self._selection.widget
        if kaa.candy.is_template(bar):
            bar = bar()
        bar.height = content.height
        bar.width = content.width
        # create grid, the location of the bar is not 100% correct
        # because of baseline is not text_height is not label.height
        w = (self.inner_width / (content.width + self.spacing)) * \
            (content.width + self.spacing)
        h = (self.inner_height / (content.height + self.spacing)) * \
            (content.height + self.spacing)
        self.grid = kaa.candy.SelectionGrid(None, (w,h), (content.width, content.height),
              'item', menu.choices, self._template, bar, 1, (self.spacing, self.spacing))
        self.grid.parent = self

    def _set_selected(self, idx, secs):
        if not self.grid:
            return
        # FIXME: add some more and better logic here
        # *****************************************************************
        # FIXME: this code is wrong when coming back from the image viewer
        # We MUST remeber how the grud looked like
        # *****************************************************************
        # we need to figure out of the user moved horizonal or vertical
        # we guess it here by choosing the shortest path
        diff = self._selected_idx - idx
        print self._selected_idx, idx, self.viewport, self._selected_pos
        if abs(diff) >= self.grid.num_cols:
            # move up or down
            self._selected_pos[1] -= diff / self.grid.num_cols
            while self._selected_pos[1] >= self.viewport[1] + self.grid.num_rows:
                self.viewport[1] += self.grid.num_rows
                self.grid.scroll_by((0, self.grid.num_rows), secs, force=True)
            while self._selected_pos[1] < self.viewport[1]:
                self.viewport[1] -= self.grid.num_rows
                self.grid.scroll_by((0, -self.grid.num_rows), secs, force=True)
        else:
            # move left or right
            self._selected_pos[0] -= diff
            while self._selected_pos[0] >= self.viewport[0] + self.grid.num_cols:
                self.viewport[0] += self.grid.num_cols
                self.grid.scroll_by((self.grid.num_cols, 0), secs, force=True)
            while self._selected_pos[0] < self.viewport[0]:
                self.viewport[0] -= self.grid.num_cols
                self.grid.scroll_by((-self.grid.num_cols, 0), secs, force=True)
        self._selected_idx = idx
        self.grid.select(self._selected_pos, secs)

# register widgets to the core
Listing.candyxml_register()
FixedSelectionListing.candyxml_register()
GridListing.candyxml_register()
