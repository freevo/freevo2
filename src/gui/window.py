# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# window.py - Clutter Stage Window
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

# python imports
import os

# kaa imports
import kaa.candy
from config import config

class Window(kaa.candy.Stage):
    """
    Window main window having the stage as child
    """
    def __init__(self):
        super(Window, self).__init__((config.display.width, config.display.height))
        self._theme_prefix = ''
        self.load_theme(config.theme, 'splash.xml')
        # This is the only child we have have.
        self.stage = self._theme.get('stage')[None]()
        self.add(self.stage)

    def load_theme(self, name=None, part=''):
        if name == None:
            name = config.theme
        if self._theme_prefix:
            for path in kaa.candy.config.imagepath[:]:
                if path.startswith(self._theme_prefix):
                    kaa.candy.config.imagepath.remove(path)
        self._theme_prefix = os.path.join(config.sharedir, 'themes', name)
        kaa.candy.config.imagepath.append(self._theme_prefix)
        info, self._theme = self.candyxml(self._theme_prefix + '/' + part)
        self._theme.icons = os.path.join(config.sharedir, 'icons', info['icons'])
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
        return kaa.candy.candyxml.parse(data, (config.stage.width, config.stage.height))

    def show_application(self, name, context=None):
        """
        Render <application> widget with the given name and the given context.
        """
        widget = self._theme.application.get(name)
        if widget:
            widget = widget(context)
        else:
            print 'no application', name
        return self.stage.show_application(widget)

    def render(self, name, style=None, context=None):
        """
        Render widget with the given name
        """
        widget = self._theme.get(name)[style](context=context)
        widget.prepare(self.stage)
        kaa.candy.thread_enter()
        self.stage.add(widget)
        kaa.candy.thread_leave()
        return widget
