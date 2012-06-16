# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# idlebar/plugin.py - Basic Idlebar plugin
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2011 Dirk Meyer, et al.
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

# freevo imports
from ... import core as freevo
from ... import gui

# get logging object
log = logging.getLogger()

class Widget(gui.Widget):
    """
    Idlebar candy widget
    """

    candyxml_style = 'idlebar'

    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        self.plugins = self.get_widget('plugins')

    def connect(self, plugin):
        """
        Connect an idlebar plugin
        """
        plugin.connect(self.plugins)

    def sync_layout(self, size):
        """
        Sync layout changes and calculate intrinsic size based on the
        parent's size.
        """
        super(Widget, self).sync_layout(size)
        x0, x1 = 0, self.plugins.width
        for widget in self.plugins.children:
            step = widget.intrinsic_size[0] + 20 # FIXME: using padding variable from theme
            if widget.xalign == widget.ALIGN_RIGHT:
                widget.x = x1 - widget.width
                x1 -= step
            else:
                widget.x = x0
                x0 += step


class PluginInterface(freevo.Plugin):
    """
    Generic plugin showing the idlebar itself
    """
    def plugin_activate(self, level):
        """
        init the idlebar
        """
        # register for signals
        freevo.signals['application-change'].connect(self.application_change)
        self.widget = None

    def application_change(self, app):
        if not self.widget:
            self.widget = gui.show_widget('idlebar')
            if not self.widget:
                return
            for p in IdleBarPlugin.plugins():
                self.widget.connect(p)
        fullscreen = app.has_capability(freevo.CAPABILITY_FULLSCREEN)
        self.widget.visible = not fullscreen

    def show(self):
        self.widget.visible = True


class IdleBarPlugin(freevo.Plugin):
    """
    A plugin for the idlebar
    """
    def __init__(self):
        super(IdleBarPlugin, self).__init__()
        if not freevo.get_plugin('idlebar'):
            freevo.activate_plugin('idlebar')

    @staticmethod
    def plugins():
        """
        Static function to return all IdlebarPlugins.
        """
        return IdleBarPlugin.plugin_list

# register the new plugin type
freevo.register_plugin(IdleBarPlugin)
