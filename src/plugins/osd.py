# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# osd.py - An osd for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin is an osd for freevo. It displays the message send by the
# event OSD_MESSAGE
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003-2006 Dirk Meyer, et al.
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
from kaa.notifier import OneShotTimer, EventHandler

# freevo imports
from freevo.ui import plugin, gui
from freevo.ui.gui import theme, widgets
from freevo.ui.config import config

from freevo.ui.event import OSD_MESSAGE

# get logging object
log = logging.getLogger()


class PluginInterface(plugin.Plugin):
    """
    osd plugin.

    This plugin shows messages send from other parts of Freevo on
    the screen for 2 seconds.

    activate with plugin.activate('plugin.osd')
    """
    def __init__(self):
        """
        init the osd
        """
        plugin.Plugin.__init__(self)
        EventHandler(self.eventhandler).register([ OSD_MESSAGE ])
        self.message = ''
        self.gui_object = None
        self.hide_timer = OneShotTimer(self.hide)


    def update(self):
        """
        update the display
        """
        display = gui.get_display()
        if self.gui_object:
            # remove the current text from the display
            self.gui_object.unparent()
            self.gui_object = None

        if not self.message:
            # if we don't have a text right now,
            # update the display without the old message
            display.update()
            return

        # get the osd from from the settings
        font = theme.font('osd')

        overscan = config.gui.display.overscan

        # create the text object
        y = overscan.y + 10
        if plugin.getbyname('idlebar') != None:
            y += 60


        self.gui_object = widgets.Text(self.message, (overscan.x, y),
                                       (display.width - 10 - 2 * overscan.x,
                                        overscan.y + 10 + font.height),
                                       font, align_h='right')

        # make sure the object is on top of everything else
        self.gui_object.set_zindex(200)

        # add the text and update the display
        display.add_child(self.gui_object)
        display.update()


    def eventhandler(self, event):
        """
        catch OSD_MESSAGE and display it, return False, maybe someone
        else is watching for the event.
        """
        if event == OSD_MESSAGE:
            self.message = event.arg
            # Start hide timer for 2 seconds. If already active, the timer
            # wil be reset.
            self.hide_timer.start(2)
            self.update()
        return True


    def hide(self):
        """
        Hide the osd
        """
        self.message = ''
        self.update()
        return False
