# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# OptionBox.py - A drop-down box.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.13  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.12  2004/02/18 21:52:04  dischi
# Major GUI update:
# o started converting left/right to x/y
# o added Window class as basic for all popup windows which respects the
#   skin settings for background
# o cleanup on the rendering, not finished right now
# o removed unneeded files/functions/variables/parameter
# o added special button skin settings
#
# Some parts of Freevo may be broken now, please report it to be fixed
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al.
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

from GUIObject import *
from ListBox   import *
from Button    import *


class OptionBox(Button):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      Letter to hold.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    selected_bg_color  Background color (Color)
    selected_fg_color  Foreground color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer

    """

    
    def __init__(self, text=' ', left=None, top=None, width=100, height=25, 
                 bg_color=None, fg_color=None, selected_bg_color=None,
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None):

        handler = None

        Button.__init__(self, text, handler, left, top, width, height, bg_color,
                        fg_color, selected_bg_color, selected_fg_color,
                        border, bd_color, bd_width)

        self.max_visible = 5
        self.h_spacing   = 6
        self.h_margin    = 6
        self.v_margin    = 2


        self.label.h_align = Align.LEFT

        self.list = ListBox(width=self.width, height=self.height*self.max_visible)
        self.add_child(self.list)
        self.list.visible = 0


    def change_item(self, direction):
        self.list.sort_items()
        self.list.scroll(direction)

        if self.list.get_selected_index() >= 0:
            self.set_text(self.list.get_selected_item().text)
        

    def add_item(self, text, value=None):
        self.list.add_item(None, text, value, h_margin=10)


    def toggle_selected_index(self, i):
        if self.list:
            self.list.toggle_selected_index(i)


    def toggle_box(self):
        if self.list.is_visible():
            self.list.visible = 0
            self.selected = 1
        else:
            self.list.visible = 1
            self.selected = 0


    def _draw(self):
        """
        The actual internal draw function.

        """
        if not self.width or not self.height or not self.text:
            raise TypeError, 'Not all needed variables set.'

        if self.selected:
            c = self.selected_bg_color.get_color_sdl()
            a = self.selected_bg_color.get_alpha()
        else:
            c = self.bg_color.get_color_sdl()
            a = self.bg_color.get_alpha()

        self.surface = self.osd.Surface(self.get_size(), 0, 32)
        self.surface.fill(c)
        self.surface.set_alpha(a)

        ar_1 = (self.width-18, 7)
        ar_2 = (self.width-8, 7)
        ar_3 = (self.width-13, 18)

        if self.selected:
            arrow_color = self.selected_fg_color.get_color_sdl()
        else:
            arrow_color = self.fg_color.get_color_sdl()

        self.osd.polygon(self.surface, arrow_color, [ar_1, ar_2, ar_3])

        if isinstance(self.list, ListBox):
            self.list.set_position(self.left, self.top+self.height)

        Container._draw(self)
        self.blit_parent()
        if self.list:
            self.list.draw(self.parent.surface)
    
