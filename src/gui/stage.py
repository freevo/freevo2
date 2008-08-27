# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# stage.py - Clutter Stage Window
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
from kaa.utils import property

import kaa.candy
from config import config

class Stage(kaa.candy.Group):
    """
    A stage holds all gui objects and keeps track of aspect ratio nand overscan
    based scalling. This object is not based on a kaa.candy.Stage but is a
    kaa.candy.Group instead.
    """

    candyxml_name = 'stage'

    def __init__(self, pos=None, size=None, context=None):
        super(Stage, self).__init__((config.stage.x, config.stage.y),
             (config.stage.width, config.stage.height))
        if config.stage.scale != 1.0:
            self._queue_sync_properties('monitor-aspect')
        self._screen = None

    def _candy_sync_properties(self):
        """
        Set some simple properties of the clutter.Actor
        """
        super(Stage, self)._candy_sync_properties()
        if 'monitor-aspect' in self._sync_properties:
            self._obj.set_scale(1.0, config.stage.scale)

    def swap(self, widget):
        """
        Replace current widget with new one
        """
        if self._screen:
            self._screen.parent = None

    def show_application(self, widget):
        """
        Show <application> widget
        """
        if widget:
            widget.width = self.width
            widget.height = self.height
            widget.prepare(self)
        try:
            kaa.candy.thread_enter()
            if widget:
                widget.parent = self
            self.swap(widget)
            self._screen = widget
        finally:
            kaa.candy.thread_leave()
        return widget


class ZoomStage(Stage):
    """
    Stage showing a zoom animation on application change.
    """

    candyxml_style = 'zoom'

    def swap(self, widget):
        """
        Replace current widget with new one
        """
        if self._screen:
            self._screen.depth += 1
            self._screen.anchor_point = self.width / 2, self.height / 2
            a = self._screen.animate(0.5, unparent=True)
            a.behave('scale', (1, 1), (1.5, 1.5)).behave('opacity', 255, 0)

Stage.candyxml_register()
ZoomStage.candyxml_register()
