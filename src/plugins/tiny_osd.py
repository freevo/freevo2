# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# time_osd.py - An osd for Freevo
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#   This plugin is an osd for freevo. It displays the message send by the
#   event OSD_MESSAGE
#
#   This file should be called osd.py, but this conflicts with the global
#   osd.py. This global file should be renamed, because it's no osd, it's
#   a render engine
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.13  2004/08/01 10:49:06  dischi
# move to new gui code
#
# Revision 1.12  2004/07/24 12:23:39  dischi
# deactivate plugin
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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
# ----------------------------------------------------------------------- */


import config
import plugin
import gui
import rc

from event import OSD_MESSAGE


class PluginInterface(plugin.DaemonPlugin):
    """
    osd plugin.

    This plugin shows messages send from other parts of Freevo on
    the screen for 2 seconds.

    activate with plugin.activate('plugin.tiny_osd')
    """
    def __init__(self):
        """
        init the osd
        """
        plugin.DaemonPlugin.__init__(self)
        self.message    = ''
        self.gui_object = None
        self.active     = False
        

    def update(self):
        """
        update the screen
        """
        screen = gui.get_screen()
        if self.gui_object:
            # remove the current text from the screen
            self.gui_object.screen.remove(self.gui_object)
            self.gui_object = None

        if not self.message:
            # if we don't have a text right now,
            # update the screen without the old message
            screen.update()
            return

        # get the osd from from the settings
        font = gui.get_font('osd')

        # create the text object
        # FIXME: do respect the idlebar if active
        self.gui_object = gui.Text(config.OSD_OVERSCAN_X,
                                   config.OSD_OVERSCAN_Y + 10,
                                   screen.width - 10 - 2 * config.OSD_OVERSCAN_X,
                                   config.OSD_OVERSCAN_Y + 10 + font.height, 
                                   self.message, font, align_h='right')

        # make sure the object is on top of everything else
        self.gui_object.layer = 20

        # add the text and update the screen
        screen.add(self.gui_object)
        screen.update()


    def eventhandler(self, event, menuw=None):
        """
        catch OSD_MESSAGE and display it, return False, maybe someone
        else is watching for the event.
        """
        if event == OSD_MESSAGE:
            self.message = event.arg
            if self.active:
                # a not used callback is active, remove it
                rc.unregister(self.hide)
            # register a callback in 2 seconds for hiding
            rc.register(self.hide, False, 200)
            self.active = True
            self.update()
        return False


    def hide(self):
        """
        Hide the osd
        """
        self.message = ''
        self.active  = False
        self.update()
