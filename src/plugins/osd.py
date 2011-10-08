# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# osd.py - An osd for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin is an OSD for freevo. It displays the message send by the
# event OSD_MESSAGE.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003-2008 Dirk Meyer, et al.
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
import logging

# kaa imports
import kaa

# freevo imports
from .. import core as freevo
from .. import gui

# get logging object
log = logging.getLogger()


class PluginInterface(freevo.Plugin):
    """
    OSD plugin.

    This plugin shows messages send by other parts of Freevo on the
    screen for 2 seconds.
    """
    def __init__(self):
        """
        init the osd
        """
        super(PluginInterface, self).__init__()
        kaa.EventHandler(self.show).register([ freevo.OSD_MESSAGE ])
        self.widget = None
        self.hide_timer = kaa.OneShotTimer(self.hide)

    def show(self, event):
        """
        Catch OSD_MESSAGE and display it
        """
        if self.widget is not None:
            self.widget.destroy()
        self.widget = gui.show_widget('osd', context={'message': event.arg})
        self.widget.show()
        # Start hide timer for 2 seconds.
        # If already active, the timer will be reset.
        self.hide_timer.start(2)

    def hide(self):
        """
        Hide the osd
        """
        self.widget.destroy()
        self.widget = None
