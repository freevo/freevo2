# -*- coding: iso-8859-1 -*-
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
# Revision 1.14  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.13  2004/02/18 21:52:04  dischi
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
from Color     import *
from Border    import *


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

        _debug_('SB: a,b,c = %s,%s,%s' % (a, b, c), 2)

        if a == 100 or b == 100 or c == 100:
            return self.get_rect()

        if self.orientation == 'vertical':
            fg_width = self.width
            fg_height = b * self.height / 100
            # fg_x = self.left
            fg_x = 0
            # fg_y = self.top + (a * self.height / 100)
            fg_y = (a * self.height / 100)
        else:
            fg_width = b * self.width / 100
            fg_height = self.height
            # fg_x = self.left + (a * self.width / 100)
            fg_x = (a * self.width / 100)
            # fg_y = self.top
            fg_y = 0

        _debug_('SB: handle_rect = %s,%s,%s,%s' % (fg_x, fg_y, fg_width, fg_height), 2)
        return (fg_x, fg_y, fg_width, fg_height)


    def get_handle_size(self):
        (a, b, c, d) = self.get_handle_rect()
        # print 'SB: get_handle_size: c,d="%s,%s"' % (c, d)
        return (c, d)


    def get_handle_coords(self):
        (a, b, c, d) = self.get_handle_rect()
        # print 'SB: get_handle_coords: a,b="%s,%s"' % (a, b)
        return (a, b)


    def calculate_position(self):
       
        if self.orientation == 'vertical':
            self.width = self.thickness
            self.height = self.parent.height
            if self.parent.show_h_scrollbar:
                self.height = self.height - self.parent.h_scrollbar.thickness
            self.left = self.parent.width - self.width
            # self.top = self.parent.top
            self.top = 0
        else:
            self.width = self.parent.width
            if self.parent.show_v_scrollbar:
                self.width = self.width - self.parent.v_scrollbar.thickness
            self.height = self.thickness
            # self.left = self.parent.left
            self.left = 0
            self.top = self.parent.height - self.height

        if isinstance(self.border, Border):
            # self.border.set_position(self.left, self.top)
            self.border.set_position(0, 0)
            self.border.width = self.width
            self.border.height = self.height

        if config.DEBUG > 1:
            print 'SB: parent_rect = %s,%s,%s,%s' % (self.parent.left, self.parent.top,
                                                     self.parent.width, self.parent.height)
            print 'SB: self_rect = %s,%s,%s,%s' % (self.left, self.top, self.width,
                                                   self.height)


    def _draw(self):
        """
        The actual internal draw function.

        """
        # if not self.width or not self.height:
        #     raise TypeError, 'Not all needed variables set.'

        self.calculate_position()

        bg_c = self.bg_color.get_color_sdl()
        bg_a = self.bg_color.get_alpha()

        self.surface = self.osd.Surface(self.get_size(), 0, 32)
        self.surface.fill(bg_c)
        self.surface.set_alpha(bg_a)

        fg_c = self.fg_color.get_color_sdl()
        _debug_('SB: fg_c = %s,%s,%s,%s' % fg_c, 2)
        fg_a = self.fg_color.get_alpha()

        fg_box = self.osd.Surface(self.get_handle_size(), 0, 32)
        fg_box.fill(fg_c)
        fg_box.set_alpha(fg_a)

        self.surface.blit(fg_box, self.get_handle_coords())
        if self.border:
            self.border.draw()

        _debug_('SB::_draw: pos=%s,%s' % (self.left, self.top), 2)
        self.blit_parent()


    

