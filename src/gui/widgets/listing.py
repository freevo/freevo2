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
from kaa.candy import Label

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

    def _candy_prepare_render(self):
        """
        Prepare rendering
        """
        super(Listing, self)._candy_prepare_render()
        if self.grid:
            return
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
        menu.rows = self.grid.num_rows
        menu.cols = self.grid.num_cols
        # now add some animations
        if self._selection.properties.get('color'):
            self.grid.behave('color', content.color,
                self._selection.properties.get('color'))
        self._set_selected(menu.selected_pos, 0)

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

# register widget to the core
Listing.candyxml_register()
FixedSelectionListing.candyxml_register()
