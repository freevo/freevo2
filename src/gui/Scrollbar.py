#if 0 /*
# -----------------------------------------------------------------------
# Scrollbar.py - A scrollbar to use with any RegionScroller.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/04/24 19:56:29  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.6  2003/03/30 20:50:00  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.5  2003/03/30 18:19:53  rshortt
# Adding self to the other GetPopupBoxStyle calls.
#
# Revision 1.4  2003/03/23 23:18:11  rshortt
# Uses skin properties now.
#
# Revision 1.3  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
#
# Revision 1.2  2003/02/23 18:21:50  rshortt
# Some code cleanup, better OOP, influenced by creating a subclass of
# RegionScroller called ListBox.
#
# Revision 1.1  2003/02/18 13:40:53  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
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
from Color     import *
from Border    import *
from Label     import * 
from types     import * 
from osd import Font

DEBUG = 0


class Scrollbar(GUIObject):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    """

    
    def __init__(self, parent, orientation, thickness=10, left=None, top=None,
                 width=None, height=None, bg_color=None, fg_color=None,
                 border=None, bd_color=None, bd_width=1):

        if orientation != "vertical" and orientation != "horizontal":
            raise TypeError, 'orientation'
        
        GUIObject.__init__(self, left, top, width, height)

        self.orientation = orientation
        self.bg_color    = bg_color
        self.fg_color    = fg_color
        self.thickness   = thickness
        self.border      = border
        self.bd_color    = bd_color
        self.bd_width    = bd_width


        if not self.bg_color:
            if self.skin_info_widget.rectangle.bgcolor:
                self.bg_color = Color(self.skin_info_widget.rectangle.bgcolor)
            else:
                self.bg_color = Color(self.osd.default_bg_color)

        if not self.fg_color:
            if self.skin_info_widget.font.color:
                self.fg_color = Color(self.skin_info_widget.font.color)
            else:
                self.fg_color = Color(self.osd.default_fg_color)

        if not self.bd_color: 
            if self.skin_info_widget.rectangle.color:
                self.bd_color = Color(self.skin_info_widget.rectangle.color)
            else:
                self.bd_color = Color(self.osd.default_fg_color)

        if not self.border:   
            self.border = Border(self, Border.BORDER_FLAT,
                                 self.bd_color, self.bd_width)


    def set_handle_position(self, pos):
        self.handle_position = pos


    def get_handle_rect(self):
        (a, b, c) = self.parent.get_view_percent(self.orientation)

        # print 'a,b,c="%s,%s,%s"' % (a, b, c)

        if a == 100 or b == 100 or c == 100:
            return self.get_rect()

        if self.orientation == 'vertical':
            fg_width = self.width
            fg_height = b * self.height / 100
            fg_x = self.left
            fg_y = self.top + (a * self.height / 100)
        else:
            fg_width = b * self.width / 100
            fg_height = self.height
            fg_x = self.left + (a * self.width / 100)
            fg_y = self.top

        return (fg_x, fg_y, fg_width, fg_height)


    def get_handle_size(self):
        (a, b, c, d) = self.get_handle_rect()
        # print 'get_handle_size: c,d="%s,%s"' % (c, d)
        return (c, d)


    def get_handle_coords(self):
        (a, b, c, d) = self.get_handle_rect()
        # print 'get_handle_coords: a,b="%s,%s"' % (a, b)
        return (a, b)


    def calculate_position(self):
       
        if self.orientation == 'vertical':
            self.width = self.thickness
            self.height = self.parent.height
            if self.parent.show_h_scrollbar:
                self.height = self.height - self.parent.h_scrollbar.thickness
            self.left = self.parent.left + self.parent.width - self.width
            self.top = self.parent.top
        else:
            self.width = self.parent.width
            if self.parent.show_v_scrollbar:
                self.width = self.width - self.parent.v_scrollbar.thickness
            self.height = self.thickness
            self.left = self.parent.left
            self.top = self.parent.top + self.parent.height - self.height

        if isinstance(self.border, Border):
            self.border.set_position(self.left, self.top)
            self.border.width = self.width
            self.border.height = self.height


    def _draw(self):
        """
        The actual internal draw function.

        """
        if not self.width or not self.height:
            raise TypeError, 'Not all needed variables set.'

        bg_c = self.bg_color.get_color_sdl()
        bg_a = self.bg_color.get_alpha()

        bg_box = pygame.Surface(self.get_size(), 0, 32)
        bg_box.fill(bg_c)
        bg_box.set_alpha(bg_a)

        fg_c = self.fg_color.get_color_sdl()
        # print 'fg_c="%s,%s,%s,%s"' % fg_c
        fg_a = self.fg_color.get_alpha()

        fg_box = pygame.Surface(self.get_handle_size(), 0, 32)
        fg_box.fill(fg_c)
        fg_box.set_alpha(fg_a)

        # bg_box.blit(fg_box, self.get_handle_coords())
        self.osd.screen.blit(bg_box, self.get_position())
        self.osd.screen.blit(fg_box, self.get_handle_coords())

        if self.border: self.border.draw()

    

