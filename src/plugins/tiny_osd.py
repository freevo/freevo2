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
# Revision 1.12  2004/07/24 12:23:39  dischi
# deactivate plugin
#
# Revision 1.11  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.10  2004/02/14 13:05:04  dischi
# do not call skin.get_singleton() anymore
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


import os
import sys
import copy
import rc

import config
import skin
import plugin

from event import *


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
        self.reason = 'not working while gui rebuild'
        return
        plugin.DaemonPlugin.__init__(self)
        self.poll_interval   = 200
        self.plugins = None
        plugin.register(self, 'osd')
        self.visible = True
        self.message = ''
        # set to 2 == we have no idea right now if
        # we have an idlebar
        self.idlebar_visible = 2
        self.poll_menu_only  = False
        

    def draw(self, (type, object), renderer):
        """
        draw current message
        """
        if not self.message:
            return

        # check for the idlebar plugin
        if self.idlebar_visible == 2:
            self.idlebar_visible = plugin.getbyname('idlebar')

        try:
            font  = renderer.get_font('osd')
        except AttributeError:
            font  = skin.get_font('osd')

        w = font.stringsize(self.message)

        if type == 'osd':
            x = config.OSD_OVERSCAN_X
            y = config.OSD_OVERSCAN_Y

            renderer.drawstringframed(self.message, config.OSD_OVERSCAN_X,
                                      config.OSD_OVERSCAN_Y + 10,
                                      renderer.width - 10 - 2 * config.OSD_OVERSCAN_X, -1,
                                      font, align_h='right', mode='hard')

        else:
            y = renderer.y + 10
            if self.idlebar_visible:
                y += 60

            renderer.drawstring(self.message, font, None,
                                (renderer.x + renderer.width-w - 10), y,
                                w, -1, 'right', 'center')



    def eventhandler(self, event, menuw=None):
        """
        catch OSD_MESSAGE and display it, return False, maybe someone
        else is watching for the event.
        """
        if event == OSD_MESSAGE:
            self.poll_counter = 1
            self.message = event.arg
            if not rc.app() or not skin.get_singleton().force_redraw:
                skin.redraw()
            elif hasattr(rc.app(), 'im_self') and hasattr(rc.app().im_self, 'redraw'):
                rc.app().im_self.redraw()
        return False

    
    def poll(self):
        """
        clear the osd after 2 seconds
        """
        if self.message:
            self.message = ''
            if not rc.app() or not skin.get_singleton().force_redraw:
                skin.redraw()
            elif hasattr(rc.app(), 'im_self') and hasattr(rc.app().im_self, 'redraw'):
                rc.app().im_self.redraw()
