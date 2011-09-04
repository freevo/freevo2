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

# freevo imports
from ... import core as freevo
from ... import gui

# get logging object
log = logging.getLogger()

class PluginInterface(freevo.Plugin):
    """
    """
    def plugin_activate(self, level):
        """
        init the idlebar
        """
        # register for signals
        freevo.signals['application-change'].connect(self._app_change)
        self.widget = None

    def _app_change(self, app):
        if not self.widget:
            self.widget = gui.show_widget('idlebar')
            if not self.widget:
                return
            for p in IdleBarPlugin.plugins():
                self.widget.connect(p)
        fullscreen = app.has_capability(freevo.CAPABILITY_FULLSCREEN)
        self.widget.visible = not fullscreen


class IdleBarPlugin(freevo.Plugin):
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

freevo.register_plugin(IdleBarPlugin)
