#if 0 /*
#  -*- coding: iso-8859-1 -*-
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
# Revision 1.4  2003/11/21 11:45:02  dischi
# render option for appliactions (not perfect)
#
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
#endif

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
            try:
                font  = skin.get_singleton().settings.font['osd']
            except:
                font  = skin.get_singleton().settings.font['default']

        w = font.font.stringsize(self.message)

        if type == 'osd':
            x = config.OVERSCAN_X
            y = config.OVERSCAN_Y

            renderer.drawstringframed(self.message, config.OVERSCAN_X,
                                      config.OVERSCAN_Y + 10,
                                      renderer.width - 2 * config.OVERSCAN_X, -1,
                                      font.font, fgcolor=0xffffff, bgcolor=0xa0000000,
                                      align_h='right', mode='hard')

        else:
            y = renderer.y + 10
            if self.idlebar_visible:
                y += 60

            renderer.write_text(self.message, font, None,
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
            if not rc.app():
                skin.get_singleton().redraw()
            elif hasattr(rc.app(), 'im_self') and hasattr(rc.app().im_self, 'redraw'):
                rc.app().im_self.redraw()
        return False

    
    def poll(self):
        """
        clear the osd after 2 seconds
        """
        if self.message:
            self.message = ''
            if not rc.app():
                skin.get_singleton().redraw()
            elif hasattr(rc.app(), 'im_self') and hasattr(rc.app().im_self, 'redraw'):
                rc.app().im_self.redraw()
