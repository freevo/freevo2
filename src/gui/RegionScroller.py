#if 0 /*
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
# Revision 1.7  2003/03/30 18:19:53  rshortt
# Adding self to the other GetPopupBoxStyle calls.
#
# Revision 1.6  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
#
# Revision 1.5  2003/03/05 03:53:34  rshortt
# More work hooking skin properties into the GUI objects, and also making
# better use of OOP.
#
# ListBox and others are working again, although I have a nasty bug regarding
# alpha transparencies and the new skin.
#
# Revision 1.4  2003/02/24 11:58:28  rshortt
# Adding OptionBox and optiondemo.  Also some minor cleaning in a few other
# objects.
#
# Revision 1.3  2003/02/23 18:21:50  rshortt
# Some code cleanup, better OOP, influenced by creating a subclass of RegionScroller called ListBox.
#
# Revision 1.2  2003/02/19 00:58:18  rshortt
# Added scrolldemo.py for a better demonstration.  Use my audioitem.py
# to test.
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
from Scrollbar import *
from Color     import *
from Border    import *
from Label     import * 
from types     import * 
from osd import Font

DEBUG = 0


class RegionScroller(GUIObject):
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

    
    def __init__(self, surface=None, left=None, top=None, width=300, 
                 height=160, bg_color=None, fg_color=None, border=None, 
                 bd_color=None, bd_width=None, show_h_scrollbar=None, 
                 show_v_scrollbar=None):

        self.surface          = surface
        self.border           = border
        self.bd_color         = bd_color
        self.bd_width         = bd_width
        self.bg_color         = bg_color
        self.fg_color         = fg_color
        self.show_h_scrollbar = show_h_scrollbar
        self.show_v_scrollbar = show_v_scrollbar

        GUIObject.__init__(self, left, top, width, height,
                           self.bg_color, self.fg_color)


        self.skin = skin.get_singleton()

        (BLAH, BLAH, BLAH, BLAH,
         button_default, BLAH) = self.skin.GetPopupBoxStyle(self)

        if not self.bd_color: 
            if button_default.rectangle.color:
                self.bd_color = Color(button_default.rectangle.color)
            else:
                self.bd_color = Color(self.osd.default_fg_color)

        if not self.bd_width: 
            if button_default.rectangle.size:
                self.bd_width = button_default.rectangle.size
            else:
                self.bd_width = 2

        if not self.border:   
            self.border = Border(self, Border.BORDER_FLAT,
                                 self.bd_color, self.bd_width)


        if self.show_h_scrollbar != 0 and not self.show_h_scrollbar:
            self.show_h_scrollbar = 1
        if self.show_v_scrollbar != 0 and not self.show_v_scrollbar:
            self.show_v_scrollbar = 1


        self.set_surface(surface)
        self.x_scroll_interval = 25
        self.y_scroll_interval = 25
        self.h_margin = 2
        self.v_margin = 2


        self.v_scrollbar = Scrollbar(self, 'vertical')
        self.add_child(self.v_scrollbar)
        self.h_scrollbar = Scrollbar(self, 'horizontal')
        self.add_child(self.h_scrollbar)

        self.filler = pygame.Surface((self.v_scrollbar.thickness, self.h_scrollbar.thickness), 0, 32)
        filler_c = Color((0,0,0,255))
        fc_c = filler_c.get_color_sdl()
        fc_a = filler_c.get_alpha()
        self.filler.fill(fc_c)
        self.filler.set_alpha(fc_a)

        if self.show_v_scrollbar:
            if self.v_scrollbar: self.v_scrollbar.calculate_position()

        if self.show_h_scrollbar:
            if self.h_scrollbar: self.h_scrollbar.calculate_position()


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
        if DEBUG: print 'scrolldir: direction="%s"' % direction

        if direction == "RIGHT":
            new_x = self.v_x + self.x_scroll_interval
            if new_x > self.max_x_offset:
                new_x = self.max_x_offset
            self.v_x = new_x
        elif direction == "LEFT":
            new_x = self.v_x - self.x_scroll_interval
            if new_x < 0:
                new_x = 0
            self.v_x = new_x
        elif direction == "DOWN":
            new_y = self.v_y + self.y_scroll_interval
            if new_y > self.max_y_offset:
                new_y = self.max_y_offset
            self.v_y = new_y
        elif direction == "UP":
            new_y = self.v_y - self.y_scroll_interval
            if new_y < 0:
                new_y = 0
            self.v_y = new_y
        if DEBUG: self.print_stuff()


    def set_surface(self, surface):
        self.surface = surface

        (None, None, self.s_w, self.s_h) = self.surface_rect = self.surface.get_rect()

        self.v_x = 0
        self.v_y = 0
        self.max_x_offset = self.s_w - self.width
        self.max_y_offset = self.s_h - self.height


    def get_location(self):
        # return self.view_coords
        return (self.v_x, self.v_y)


    def _draw(self):
        """
        The actual internal draw function.

        """
        if not self.width or not self.height or not self.surface:
            raise TypeError, 'Not all needed variables set.'

        (x, y) = self.get_location()
        box = self.surface.subsurface(x, y, self.width, self.height)

        self.osd.screen.blit(box, self.get_position())

        if self.show_v_scrollbar:
            if self.v_scrollbar: self.v_scrollbar.draw()

        if self.show_h_scrollbar:
            if self.h_scrollbar: self.h_scrollbar.draw()

        if self.show_v_scrollbar and self.show_h_scrollbar:
            self.osd.screen.blit(self.filler,
                             (self.left+self.width-self.v_scrollbar.thickness,
                              self.top+self.height-self.h_scrollbar.thickness))

        if self.border: self.border.draw()

    

    def set_border(self, bs):
        """
        bs  Border style to create.
        
        Set which style to draw border around object in. If bs is 'None'
        no border is drawn.
        
        Default is to have no border.
        """
        if isinstance(self.border, Border):
            self.border.set_style(bs)
        elif not bs:
            self.border = None
        else:
            self.border = Border(self, bs)
            

    def set_position(self, left, top):
        """
        Overrides the original in GUIBorder to update the border as well.
        """
        GUIObject.set_position(self, left, top)
        if isinstance(self.border, Border):
            if DEBUG: print "updating borders set_postion as well"
            self.border.set_position(left, top)

        if self.show_h_scrollbar:
            if self.h_scrollbar: self.h_scrollbar.calculate_position()
        if self.show_v_scrollbar:
            if self.v_scrollbar: self.v_scrollbar.calculate_position()
        

    def _erase(self):
        """
        Erasing us from the canvas without deleting the object.
        """

        if DEBUG: print "  Inside PopupBox._erase..."
        # Only update the part of screen we're at.
        self.osd.screen.blit(self.bg_image, self.get_position(),
                        self.get_rect())
        
        if self.border:
            if DEBUG: print "    Has border, doing border erase."
            self.border._erase()

        if DEBUG: print "    ...", self


    def eventhandler(self, event):

        scrolldirs = [self.rc.UP, self.rc.DOWN, self.rc.LEFT, self.rc.RIGHT]
        if scrolldirs.count(event) > 0:
            self.scroll(event)
            self.draw()
            self.osd.update(self.get_rect())
            return
        else:
            return self.parent.eventhandler(event)


