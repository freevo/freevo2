#if 0 /*
# -----------------------------------------------------------------------
# ListBox.py - scrollable box containing ListItems.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/02/23 18:24:04  rshortt
# New classes.  ListBox is a subclass of RegionScroller so that it can scroll though a list of ListItems which are drawn to a surface.  Also included is a listboxdemo to demonstrate and test everything.
#
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

from GUIObject      import *
from Scrollbar      import *
from RegionScroller import *
from Color          import *
from Border         import *
from Label          import * 
from ListItem       import * 
from types          import * 
from osd import     Font

DEBUG = 1


class ListBox(RegionScroller):
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
    show_h_scrollbar Integer
    show_v_scrollbar Integer
    """

    
    def __init__(self, items=[], left=None, top=None, width=None, height=None, 
                 bg_color=None, fg_color=None, selected_bg_color=None,
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None, show_h_scrollbar=None, show_v_scrollbar=None):


        self.border         = border
        self.h_margin       = 2
        self.v_margin       = 2
        self.bg_color       = bg_color
        self.fg_color       = fg_color
        self.bd_color       = bd_color
        self.bd_width       = bd_width
        self.width          = width
        self.height         = height
        self.left           = left
        self.top            = top
        self.selected_bg_color = selected_bg_color
        self.selected_fg_color = selected_fg_color
        self.show_h_scrollbar = show_h_scrollbar
        self.show_v_scrollbar = show_v_scrollbar

        if not self.width:    self.width  = 100
        if not self.height:   self.height = 200

        if self.show_h_scrollbar != 0 and not self.show_h_scrollbar:
            self.show_h_scrollbar = 0
        if self.show_v_scrollbar != 0 and not self.show_v_scrollbar:
            self.show_v_scrollbar = 1

        self.set_surface(pygame.Surface(self.get_size(), 0, 32))

        RegionScroller.__init__(self, self.surface, self.left, self.top, self.width,
                                self.height, self.border, self.bd_color,
                                self.bd_width, self.show_h_scrollbar,
                                self.show_v_scrollbar)

        if not self.bg_color: Color(self.osd.default_bg_color)
        if not self.fg_color: Color(self.osd.default_fg_color)
        if not self.selected_fg_color: self.selected_fg_color = self.fg_color
        if not self.selected_bg_color: self.selected_bg_color = Color((0,255,0,128))

        self.set_items(items)

        self.x_scroll_interval = 25
        self.y_scroll_interval = 25


    def scroll(self, direction):
        if DEBUG: print 'listbox scroll: direction="%s"' % direction

        if direction == "RIGHT" or direction == "LEFT":
            return RegionScroller.scroll(self, direction)

        elif direction == "DOWN":

            i = self.get_selected_index()
            if i < len(self.items)-1:
                self.toggle_selected_index(i)
                self.toggle_selected_index(i+1)

                # if we are all the way down
                new_select = self.get_selected_item()
                if new_select.top + new_select.height > self.v_y + self.height:
                    return RegionScroller.scroll(self, direction)

        elif direction == "UP":

            i = self.get_selected_index()
            if i > 0:
                self.toggle_selected_index(i)
                self.toggle_selected_index(i-1)

                # if we are all the way up
                new_select = self.get_selected_item()
                if new_select.top < self.v_y:
                    return RegionScroller.scroll(self, direction)

        self._draw()
        self.osd.update()


    def get_selected_index(self):
        for i in range(len(self.items)):
            if self.items[i].selected:
                return i

        return -1


    def get_selected_item(self):
        for i in range(len(self.items)):
            if self.items[i].selected:
                return self.items[i]

        return None


    def toggle_selected_index(self, i):
        if i < 0: return
        self.items[i].toggle_selected()


    def set_items(self, items):
        self.items = items
       
        for item in self.items:
            self.add_child(item)

        self.adjust_surface()


    def add_item(self, item=None, text=None, value=None):
        if not item:
            if not text:
                text = ' '
            if not value: 
                value = text

            item = ListItem(text, value, self.width, None, 
                            self.bg_color, self.fg_color, 
                            self.selected_bg_color, self.selected_fg_color)

        self.items.append(item)
        self.add_child(item)

        self.adjust_surface()


    def remove_item(self, item):
        self.items.remove(item)
        item.destroy()

        self.adjust_surface()


    def adjust_surface(self):
        x = 0
        y = 0

        for item in self.items:
            if item.width > x:
                x = item.width
            y = y + item.height

        if y < self.height:
            y = self.height
        if x < self.width:
            x = self.width

        c   = self.bg_color.get_color_sdl()
        a   = self.bg_color.get_alpha()
        self.set_surface(pygame.Surface((x, y), 0, 32))
        self.surface.fill(c)
        self.surface.set_alpha(a)


    def _draw(self):
        """
        Lets alter the surface then get our superclass to do the draw.

        """
        if not self.width or not self.height or not self.surface:
            raise TypeError, 'Not all needed variables set.'


        (x, y) = (0, 0)
        for item in self.items:
            item.set_position(x,y)
            y = y + item.height
            item._draw(self.surface)
    
        RegionScroller._draw(self)


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


    def destroy(self):
        for item in self.items:
            print 'LB.destroy: destroying %s' % item
            item.destroy()
            item = None
        self.items = []
        RegionScroller.destroy(self)


    def eventhandler(self, event):

        scrolldirs = [self.rc.UP, self.rc.DOWN, self.rc.LEFT, self.rc.RIGHT]
        if scrolldirs.count(event) > 0:
            self.scroll(event)
            return
        else:
            return self.parent.eventhandler(event)


