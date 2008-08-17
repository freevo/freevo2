# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# idlebar/plugin.py - Basic Idlebar plugin
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2007 Dirk Meyer, et al.
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

import kaa.candy

from freevo import plugin
from freevo.ui import application, config
import freevo.ui.gui

# get logging object
log = logging.getLogger()

guicfg = config.gui

class Widget(kaa.candy.Container):
    candyxml_name = 'idlebar'

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        for c in element:
            if c.ignore_overscan:
                # the idlebar background. Expand by overscan
                c._attrs['x'] = c._attrs.get('x', 0) - guicfg.display.overscan.x
                c._attrs['y'] = c._attrs.get('y', 0) - guicfg.display.overscan.y
                default = guicfg.display.width - 2 * guicfg.display.overscan.x
                value = float(c._attrs.get('width', default))
                factor = value / default
                c._attrs['width'] = int(value + factor * 2 * guicfg.display.overscan.x)
                c._attrs['height'] +=  guicfg.display.overscan.y
        return super(Widget, cls).candyxml_parse(element)

Widget.candyxml_register()

class PluginInterface(plugin.Plugin):
    """
    """
    def plugin_activate(self, level):
        """
        init the idlebar
        """
        # register for signals
        application.signals['changed'].connect(self._app_change)
        self.visible = False
        self.bar = None

    def _candy_layout(self, widgets, spacing):
        x0 = 0
        x1 = self.container.inner_width + spacing
        for widget in widgets:
            # FIXME: this code does not respect widget.padding
            if widget.xalign == widget.ALIGN_RIGHT:
                x1 -= widget._obj.get_width() - spacing
                widget._obj.set_x(x1)
            else:
                widget._obj.set_x(x0)
                x0 += widget._obj.get_width() + spacing
    
    def _app_change(self, app):
        if not self.bar:
            self.bar = freevo.ui.gui.window.render('idlebar')
            self.container = self.bar.get_widget('plugins')
            self.container.layout = self._candy_layout
            for p in IdleBarPlugin.plugins():
                p.connect(self.container)
        fullscreen = app.has_capability(application.CAPABILITY_FULLSCREEN)
        if fullscreen == self.visible:
            log.info('set visible %s' % (not fullscreen))
            if not self.visible:
                animation = self.container.animate(0.2)
                animation.behave('opacity', 0, 255)
            else:
                animation = self.container.animate(0.2)
                animation.behave('opacity', 255, 0)
            self.visible = not fullscreen
        return True


class IdleBarPlugin(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        if not plugin.getbyname('idlebar'):
            plugin.activate('idlebar')

    def plugins():
        """
        Static function to return all IdlebarPlugins.
        """
        return IdleBarPlugin.plugin_list

    plugins = staticmethod(plugins)


plugin.register(IdleBarPlugin)
