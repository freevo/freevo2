# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Window - A window for freevo.
# -----------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2004/08/24 19:23:37  dischi
# more theme updates and design cleanups
#
# Revision 1.11  2004/08/24 16:42:42  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.10  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.9  2004/08/05 17:29:14  dischi
# improved screen and eventhandler
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------

import copy

from mevas.container import CanvasContainer

import eventhandler
import gui

class Window(CanvasContainer):
    """
    """
    def __init__(self, x=None, y=None, width=None, height=None):
        CanvasContainer.__init__(self)
        self.set_zindex(100)
        
        self._display_width  = gui.get_display().width
        self._display_height = gui.get_display().height
        self.event_context   = 'input'

        self.center_on_screen = False

        if width == None:
            width  = self._display_width / 2

        if height == None:
            height = self._display_height / 4

        if x == None:
            x = self._display_width/2 - width/2

        if y == None:
            y  = self._display_height/2 - height/2
            self.center_on_screen = True

        self.content_layout    = gui.get_theme().popup.content
        self.background_layout = gui.get_theme().popup.background

        self.set_size((width, height))
        self.set_pos((x, y))
        
        self.widget_normal   = self.content_layout.types['widget']
        self.widget_selected = self.content_layout.types['selected']
        self.button_normal   = self.content_layout.types['button']
        self.button_selected = self.content_layout.types['button selected']

        self._display  = None


    def _create_background(self, screen):
        """
        The draw function.
        """
        _debug_('Window::_create_background %s' % self, 1)
        
        for o in self.background_layout:
            if o.type == 'rectangle':
                r = copy.deepcopy(o)
                r.width  = eval(str(r.width),  { 'MAX' : self.width })
                r.height = eval(str(r.height), { 'MAX' : self.height })

                if not r.width:
                    r.width  = self.width
                if not r.height:
                    r.height = self.height
                if r.x + r.width > self.width:
                    r.width = self.width - r.x
                if r.y + r.height > self.height:
                    r.height = self.height - r.y

            r = gui.Rectangle((r.x, r.y), (r.width, r.height),
                              r.bgcolor, r.size, r.color, r.radius)
            r.set_zindex(-1)
            self.add_child(r)

            
    def show(self):
        if self._display:
            return
        eventhandler.add_window(self)
        self._display = gui.get_display()
        self._create_background(self._display)
        self._display.add_child(self)
        self._display.update()


    def destroy(self):
        eventhandler.remove_window(self)
        if not self._display:
            return
        self._display.remove_child(self)
        self._display.update()
        self._display = None
