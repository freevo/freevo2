# -*- coding: iso-8859-1 -*-
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
# Revision 1.21  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.20  2004/02/18 21:52:04  dischi
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
import osd

from GUIObject      import *
from RegionScroller import *
from Button         import *
from ListItem       import * 


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

    
    def __init__(self, items=None, left=None, top=None, width=100, height=200, 
                 bg_color=None, fg_color=None, selected_bg_color=None,
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None, show_h_scrollbar=None, show_v_scrollbar=None):

        self.items             = items
        self.show_h_scrollbar  = show_h_scrollbar
        self.show_v_scrollbar  = show_v_scrollbar

        if self.show_h_scrollbar != 0 and not self.show_h_scrollbar:
            self.show_h_scrollbar = 0
        if self.show_v_scrollbar != 0 and not self.show_v_scrollbar:
            self.show_v_scrollbar = 1


        dummy_surface = osd.get_singleton().Surface((1,1), 0, 32)

        RegionScroller.__init__(self, dummy_surface, left, top, width, 
                                height, bg_color, fg_color,
                                border, bd_color, bd_width,
                                self.show_h_scrollbar, self.show_v_scrollbar)

        self.set_surface(self.osd.Surface(self.get_size(), 0, 32))

        self.h_margin                 = 2
        self.v_margin                 = 2
        self.items_height             = Button('foo').height
        self.x_scroll_interval        = 25
        self.y_scroll_interval        = self.items_height
        if not self.items: self.items = []

        if self.items: self.set_items(self.items)


    def scroll(self, direction):
        _debug_('listbox scroll: direction="%s"' % direction, 2)

        if direction in (INPUT_RIGHT, INPUT_LEFT):
            return RegionScroller.scroll(self, direction)

        elif direction == INPUT_DOWN:

            i = self.get_selected_index()
            if i < len(self.items)-1:
                self.toggle_selected_index(i)
                self.toggle_selected_index(i+1)

                # if we are all the way down
                new_select = self.get_selected_item()
                if new_select.top + new_select.height > self.v_y + self.height:
                    return RegionScroller.scroll(self, direction)

        elif direction == INPUT_UP:

            i = self.get_selected_index()
            if i > 0:
                self.toggle_selected_index(i)
                self.toggle_selected_index(i-1)

                # if we are all the way up
                new_select = self.get_selected_item()
                if new_select.top < self.v_y:
                    return RegionScroller.scroll(self, direction)


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


    def sort_items(self):
        (x, y) = (0, 0)
        for item in self.items:
            item.set_position(x,y)
            y = y + item.height


    def add_item(self, item=None, text=None, value=None, h_margin=20):
        if not item:
            if not text:
                text = ' '
            if not value: 
                value = text

            item = ListItem(text, value, self.width, self.items_height, 
                            self.bg_color, self.fg_color, 
                            self.selected_bg_color, self.selected_fg_color, 
                            h_margin=h_margin)
            if item.border:
                item.border.thickness = 1
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
        self.set_surface(self.osd.Surface((x, y), 0, 32))
        self.region_surface.fill(c)
        self.region_surface.set_alpha(a)


    def _draw(self, surface=None):
        """
        Lets alter the surface then get our superclass to do the draw.

        """

        if not self.width or not self.height or not self.region_surface:
            raise TypeError, 'Not all needed variables set.'

        self.sort_items()
        for item in self.items:
            item.draw()

        RegionScroller._draw(self, surface)


    def destroy(self):
        for item in self.items:
            item.destroy()
            item = None
        self.items = []
        RegionScroller.destroy(self)


    def eventhandler(self, event):
        _debug_('ListBox::eventhandler: event=%s' % event, 2)

        if event in (INPUT_UP, INPUT_DOWN, INPUT_LEFT, INPUT_RIGHT ):
            _debug_('ListBox::eventhandler: should scroll', 2)
            self.scroll(event)
            self.draw(update=True)
            return True
        else:
            return self.parent.eventhandler(event)


