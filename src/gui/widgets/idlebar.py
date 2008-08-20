# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# idlebar.py
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008 Dirk Meyer, et al.
#
# First edition: Dirk Meyer <dischi@freevo.org>
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

import logging

from kaa.utils import property
import kaa.candy

from .. import config

# get logging object
log = logging.getLogger()

class Idlebar(kaa.candy.Container):
    candyxml_name = 'idlebar'

    # properties
    __visible = False

    def __init__(self, *args, **kwargs):
        super(Idlebar, self).__init__(*args, **kwargs)
        self.plugins = self.get_widget('plugins')
        self.plugins.layout = self._candy_layout_plugins

    def connect(self, plugin):
        """
        Connect an idlebar plugin
        """
        plugin.connect(self.plugins)

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, visible):
        if self.__visible == visible:
            return
        if visible:
            self._show()
        else:
            self._hide()
        self.__visible = visible

    def _show(self):
        """
        Show the idlebar
        """
        animation = self.animate(0.2)
        animation.behave('opacity', 0, 255)

    def _hide(self):
        """
        Hide the idlebar
        """
        animation = self.animate(0.2)
        animation.behave('opacity', 255, 0)

    def _candy_layout_plugins(self, widgets, spacing):
        """
        Layput plugin children
        """
        x0 = 0
        x1 = self.plugins.inner_width + spacing
        for widget in widgets:
            # FIXME: this code does not respect widget.padding
            if widget.xalign == widget.ALIGN_RIGHT:
                widget._obj.set_x(x1)
                x1 -= widget._obj.get_width() - spacing
            else:
                widget._obj.set_x(x0)
                x0 += widget._obj.get_width() + spacing

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        guicfg = config.stage
        for c in element:
            if c.ignore_overscan:
                # the idlebar background. Expand by overscan
                c._attrs['x'] = c._attrs.get('x', 0) - guicfg.overscan_x
                c._attrs['y'] = c._attrs.get('y', 0) - guicfg.overscan_y
                value = float(c._attrs.get('width', guicfg.width))
                factor = value / guicfg.width
                c._attrs['width'] = int(value + factor * 2 * guicfg.overscan_x)
                c._attrs['height'] += guicfg.overscan_y
        return super(Idlebar, cls).candyxml_parse(element)

Idlebar.candyxml_register()
