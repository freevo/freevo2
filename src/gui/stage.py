# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# stage.py - Clutter Stage
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008-2011 Dirk Meyer, et al.
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

__all__ = [ 'Stage', 'config' ]

# python imports
import os
import logging

# kaa imports
import kaa.candy

# get logging object
log = logging.getLogger('gui')

class Config(object):

    def load(self, config, sharedir):
        self.freevo = config
        self.sharedir = sharedir

    def __getattr__(self, attr):
        return getattr(self.freevo.gui, attr)

# create config object
config = Config()

class Stage(kaa.candy.Stage):
    """
    Freevo main window
    """
    def __init__(self):
        super(Stage, self).__init__((int(config.display.width), int(config.display.height)), 'freevo2')
        self.theme_prefix = ''
        self.width, self.height = self.size
        # layer 0: background
        # layer 1: application
        self.add_layer()
        # layer 2: widgets
        self.add_layer()
        # layer 3: popups
        self.add_layer()
        self.app = None

    def load_theme(self, name=None, part=''):
        if name == None:
            name = config.theme
        if self.theme_prefix:
            for path in kaa.candy.config.imagepath[:]:
                if path.startswith(self.theme_prefix):
                    kaa.candy.config.imagepath.remove(path)
        self.theme_prefix = os.path.join(config.sharedir, 'themes', name)
        kaa.candy.config.imagepath.append(self.theme_prefix)
        attr, self.theme = self.candyxml(self.theme_prefix + '/' + part)
        self.theme.icons = os.path.join(config.sharedir, 'icons', attr['icons'])
        size = int(attr['geometry'].split('x')[0]), int(attr['geometry'].split('x')[1])
        scale_x = float(self.size[0] - ( 2 * config.display.overscan.x)) / size[0]
        scale_y = float(self.size[1] - ( 2 * config.display.overscan.y)) / size[1]
        for layer in self.layer[1:]:
            layer.x = config.freevo.gui.display.overscan.x
            layer.y = config.freevo.gui.display.overscan.y
            layer.scale_x = scale_x
            layer.scale_y = scale_y
        # reference theme in all widgets
        # NOTE: this bounds all widgets created from this point to the
        # same theme. Two displays with different themes are not possible.
        # On the other hand setting a theme this way is fast and simple.
        kaa.candy.Widget.theme = self.theme

    def show_application(self, name, context=None):
        """
        Render <application> widget with the given name and the given context.
        """
        app = self.theme.application.get(name)
        if not app:
            log.error('no application named %s', name)
            return None
        app = app(context)
        self.add(app, layer=1)
        if app.background:
            self.add(app.background, layer=0)
        app.show()
        if self.app:
            if self.app.background:
                self.app.background.parent = None
            self.app.destroy()
            self.app.parent = None
        self.app = app
        return app

    def show_widget(self, name, layer=2, context=None):
        """
        Render widget with the given name
        """
        try:
            widget = self.theme.get('widget')[name](context=context)
            self.add(widget, layer=layer)
            return widget
        except TypeError:
            log.error('widget %s not defined in theme', name)
