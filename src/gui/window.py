# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Window - A window for freevo.
# -----------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/10/05 19:50:54  dischi
# Cleanup gui/widgets:
# o remove unneeded widgets
# o move window and boxes to the gui main level
# o merge all popup boxes into one file
# o rename popup boxes
#
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

# python imports
import copy

# freevo imports
import eventhandler

# gui imports
from displays import get_display
from theme_engine import get_theme
from widgets import Rectangle, CanvasContainer


class Window(CanvasContainer):
    """
    """
    def __init__(self, x=None, y=None, width=None, height=None):
        CanvasContainer.__init__(self)
        self.set_zindex(100)
        
        self._display_width  = get_display().width
        self._display_height = get_display().height
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

        layout = get_theme().popup.content
        
        self.set_size((width, height))
        self.set_pos((x, y))
        
        self.widget_normal   = layout.types['widget']
        self.widget_selected = layout.types['selected']
        self.button_normal   = layout.types['button']
        self.button_selected = layout.types['button selected']
        self.content_spacing = layout.spacing
        
        self.__c_x = int(eval(str(layout.x), { 'MAX': 0}))
        self.__c_y = int(eval(str(layout.y), { 'MAX': 0}))
        self.__c_w = -int(eval(str(layout.width), { 'MAX': 0}))
        self.__c_h = -int(eval(str(layout.height), { 'MAX': 0}))
        self._display  = None


    def __create_background(self, screen):
        """
        The draw function.
        """
        _debug_('Window::__create_background %s' % self, 1)
        
        for o in get_theme().popup.background:
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

            r = Rectangle((r.x, r.y), (r.width, r.height),
                          r.bgcolor, r.size, r.color, r.radius)
            r.set_zindex(-1)
            self.add_child(r)


    def get_content_pos(self):
        return self.__c_x, self.__c_y


    def get_content_size(self):
        w, h = self.get_size()
        return w - self.__c_w, h - self.__c_h
    
            
    def show(self):
        if self._display:
            return
        eventhandler.add_window(self)
        self._display = get_display()
        self.__create_background(self._display)
        self._display.add_child(self)
        self._display.update()


    def destroy(self):
        eventhandler.remove_window(self)
        if not self._display:
            return
        self._display.remove_child(self)
        self._display.update()
        self._display = None
