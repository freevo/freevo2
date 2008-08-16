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

import os

# kaa imports
import kaa
from kaa.utils import property

import kaa.candy
from .. import config, SHAREDIR

guicfg = config.gui

class Context(kaa.candy.Group):
    def __init__(self):
        x, y = guicfg.display.overscan.x, guicfg.display.overscan.y
        w, h = guicfg.display.width - 2 * x, guicfg.display.height - 2 * y
        super(Context, self).__init__((x,y), (w,h))
        self._screen = None

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
        self.swap(widget)
        self._screen = widget
        if self._screen:
            self._screen.width = self.width
            self._screen.height = self.height
            self._screen.parent = self
        return widget

class ZoomContext(Context):

    def swap(self, widget):
        """
        Replace current widget with new one
        """
        if self._screen:
            self._screen.depth += 1
            self._screen.anchor_point = self.width / 2, self.height / 2
            a = self._screen.animate(0.5, unparent=True)
            a.behave('scale', (1, 1), (1.5, 1.5)).behave('opacity', 255, 0)

class Stage(kaa.candy.Stage):
    """
    Window main window.
    """
    def __init__(self):
        super(Stage, self).__init__((guicfg.display.width, guicfg.display.height))
        self._theme_prefix = ''
        x, y = guicfg.display.overscan.x, guicfg.display.overscan.y
        self.content = ZoomContext()
        self.content.parent = self
        self.load_theme(guicfg.theme, 'splash.xml')

    def load_theme(self, name=None, part=''):
        if name == None:
            name = guicfg.theme
        if self._theme_prefix:
            for path in kaa.candy.config.imagepath[:]:
                if path.startswith(self._theme_prefix):
                    kaa.candy.config.imagepath.remove(path)
        self._theme_prefix = os.path.join(SHAREDIR, 'themes', name)
        kaa.candy.config.imagepath.append(self._theme_prefix)
        self._theme = self.candyxml(self._theme_prefix + '/' + part)[1]
        # reference theme in all widgets
        # NOTE: this bounds all widgets created from this point to the
        # same theme. Two displays with different themes are not possible.
        # On the other hand setting a theme this way is fast and simple.
        kaa.candy.Widget.theme = self._theme

    def candyxml(self, data):
        """
        Load a candyxml file based on the given screen resolution.

        @param data: filename of the XML file to parse or XML data
        @returns: root element attributes and dict of parsed elements
        """
        return kaa.candy.candyxml.parse(data, (self.content.width, self.content.height))

    def show_application(self, name, context=None):
        """
        Render <application> widget with the given name and the given context.
        """
        widget = self._theme.application.get(name)
        if widget:
            widget = widget(context)
        else:
            print 'no application', name
        return self.content.show_application(widget)

    def render(self, name, style=None):
        """
        Render widget with the given name
        """
        widget = self._theme.get(name)[style]()
        widget.parent = self.content
        return widget

# load input plugin
from freevo import plugin
plugin.activate('input.candy')
