#if 0 /*
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
# Revision 1.8  2003/05/21 00:04:26  rshortt
# General improvements to layout and drawing.
#
# Revision 1.7  2003/05/15 02:21:54  rshortt
# got RegionScroller, ListBox, ListItem, OptionBox working again, although
# they suffer from the same label alignment bouncing bug as everything else
#
# Revision 1.6  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.5  2003/03/30 20:50:00  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.4  2003/03/30 18:19:53  rshortt
# Adding self to the other GetPopupBoxStyle calls.
#
# Revision 1.3  2003/03/24 00:37:06  rshortt
# OptionBox now uses skin properties.
#
# Revision 1.2  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
#
# Revision 1.1  2003/02/24 11:58:28  rshortt
# Adding OptionBox and optiondemo.  Also some minor cleaning in a few other
# objects.
#
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
#endif

import pygame
import config

from GUIObject import *
from ListBox   import *
from Button     import *
from Color     import *
from Border    import *
from Label     import * 
from types     import * 
from osd import Font

DEBUG = 0


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

        self.surface = pygame.Surface(self.get_size(), 0, 32)
        self.surface.fill(c)
        self.surface.set_alpha(a)

        ar_1 = (self.width-18, 7)
        ar_2 = (self.width-8, 7)
        ar_3 = (self.width-13, 18)

        if self.selected:
            arrow_color = self.selected_fg_color.get_color_sdl()
        else:
            arrow_color = self.fg_color.get_color_sdl()

        pygame.draw.polygon(self.surface, arrow_color, [ar_1, ar_2, ar_3])

        # if self.border: self.border.draw()

        # self.label.draw()

        if isinstance(self.list, ListBox):
            self.list.set_position(self.left, self.top+self.height)

        Container._draw(self)
        self.parent.surface.blit(self.surface, self.get_position())
        if self.list:   self.list.draw(self.parent.surface)
    
