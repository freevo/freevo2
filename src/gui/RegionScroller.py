# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# RegionScroller.py - A class that will scroll another surface.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.22  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.21  2004/02/18 21:52:04  dischi
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
from event import *

from GUIObject import *
from Container import *
from Scrollbar import *
from Color     import *
from Border    import *


class RegionScroller(Container):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      Letter to hold.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    show_h_scrollbar Integer
    show_v_scrollbar Integer
    """

    
    def __init__(self, region_surface=None, left=None, top=None, width=300, 
                 height=160, bg_color=None, fg_color=None, border=None, 
                 bd_color=None, bd_width=None, show_h_scrollbar=None, 
                 show_v_scrollbar=None):

        self.show_h_scrollbar = show_h_scrollbar
        self.show_v_scrollbar = show_v_scrollbar

        Container.__init__(self, 'widget', left, top, width, height, bg_color,
                           fg_color, border=border, bd_color=bd_color, 
                           bd_width=bd_width)

        self.internal_h_align = Align.NONE
        self.internal_v_align = Align.NONE

        if self.show_h_scrollbar != 0 and not self.show_h_scrollbar:
            self.show_h_scrollbar = 1
        if self.show_v_scrollbar != 0 and not self.show_v_scrollbar:
            self.show_v_scrollbar = 1


        self.set_surface(region_surface)
        self.x_scroll_interval = 25
        self.y_scroll_interval = 25
        self.h_margin = 2
        self.v_margin = 2


        self.v_scrollbar = Scrollbar(self, 'vertical')
        self.add_child(self.v_scrollbar)
        self.h_scrollbar = Scrollbar(self, 'horizontal')
        self.add_child(self.h_scrollbar)

        self.filler = self.osd.Surface((self.v_scrollbar.thickness,
                                        self.h_scrollbar.thickness), 0, 32)
        filler_c = Color((0,0,0,255))
        fc_c = filler_c.get_color_sdl()
        fc_a = filler_c.get_alpha()
        self.filler.fill(fc_c)
        self.filler.set_alpha(fc_a)

        # if self.show_v_scrollbar:
            # if self.v_scrollbar: self.v_scrollbar.calculate_position()

        # if self.show_h_scrollbar:
            # if self.h_scrollbar: self.h_scrollbar.calculate_position()


    def get_view_percent(self, orientation):
        if orientation == 'vertical':
            a = self.v_y * 100 / self.s_h 
            b = self.height * 100 / self.s_h 
            c = (self.s_h - (self.v_y + self.height)) * 100 / self.s_h 
        else:
            a = self.v_x * 100 / self.s_w 
            b = self.width * 100 / self.s_w 
            c = (self.s_w - (self.v_x + self.width)) * 100 / self.s_w 

        rem = 100 - a - b - c
        b = b + rem

        return (a, b, c)


    def print_stuff(self):
        print '  self.s_w="%s"' % self.s_w
        print '  self.s_h="%s"' % self.s_h
        print '  self.v_x="%s"' % self.v_x
        print '  self.v_y="%s"' % self.v_y
        print '  self.width="%s"' % self.width
        print '  self.height="%s"' % self.height
        print '  self.top="%s"' % self.top
        print '  self.left="%s"' % self.left
        print '  self.max_x_offset="%s"' % self.max_x_offset
        print '  self.max_y_offset="%s"' % self.max_y_offset


    def scroll(self, direction):
        _debug_('scrolldir: direction="%s"' % direction, 2)

        if direction == INPUT_RIGHT:
            new_x = self.v_x + self.x_scroll_interval
            if new_x > self.max_x_offset:
                new_x = self.max_x_offset
            self.v_x = new_x
        elif direction == INPUT_LEFT:
            new_x = self.v_x - self.x_scroll_interval
            if new_x < 0:
                new_x = 0
            self.v_x = new_x
        elif direction == INPUT_DOWN:
            new_y = self.v_y + self.y_scroll_interval
            if new_y > self.max_y_offset:
                new_y = self.max_y_offset
            self.v_y = new_y
        elif direction == INPUT_UP:
            new_y = self.v_y - self.y_scroll_interval
            if new_y < 0:
                new_y = 0
            self.v_y = new_y
        if config.DEBUG > 1:
            self.print_stuff()


    def set_surface(self, surface):
        self.region_surface = surface

        (self.s_w, self.s_h) = self.region_surface_rect \
                                         = self.region_surface.get_rect()[2:4]

        self.v_x = 0
        self.v_y = 0
        self.max_x_offset = self.s_w - self.width
        self.max_y_offset = self.s_h - self.height


    def get_location(self):
        return (self.v_x, self.v_y)


    def _draw(self, surface=None):
        """
        The actual internal draw function.

        """
        if not self.width or not self.height or not self.region_surface:
            raise TypeError, 'Not all needed variables set.'

        self.set_position(self.left,self.top)
        (x, y) = self.get_location()
        self.surface = self.osd.Surface(self.get_size(), 0, 32)
        # self.surface = self.region_surface.subsurface(x, y, self.width, self.height)
        # self.surface.fill((255,255,255,255))
        # self.surface.set_alpha(255)
        self.surface.blit(self.region_surface, (0, 0),  (x, y, self.width, self.height))


        if self.show_v_scrollbar and self.v_scrollbar:
            self.v_scrollbar.draw()

        if self.show_h_scrollbar and self.h_scrollbar:
            self.h_scrollbar.draw()

        if self.show_v_scrollbar and self.show_h_scrollbar:
            self.surface.blit(self.filler,
                             (self.width-self.v_scrollbar.thickness,
                              self.height-self.h_scrollbar.thickness))

        if self.border:
            self.border.draw()

        if surface:
            surface.blit(self.surface, self.get_position())
        else:
            self.blit_parent()
    

    def set_position(self, left, top):
        """
        Overrides the original in GUIBorder to update the border as well.
        """
        GUIObject.set_position(self, left, top)
        if isinstance(self.border, Border):
            _debug_("updating borders set_postion as well", 2)
            self.border.set_position(left, top)

        # if self.show_h_scrollbar:
            # if self.h_scrollbar: self.h_scrollbar.calculate_position()
        # if self.show_v_scrollbar:
            # if self.v_scrollbar: self.v_scrollbar.calculate_position()
        

    def eventhandler(self, event):

        if event in (INPUT_UP, INPUT_DOWN, INPUT_LEFT, INPUT_RIGHT ):
            self.scroll(event)
            self.parent.draw(update=True)
            return
        else:
            return self.parent.eventhandler(event)


