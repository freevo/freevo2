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
# Revision 1.18  2003/09/13 10:32:55  dischi
# fix a font problem and cleanup some unneeded stuff
#
# Revision 1.17  2003/09/07 11:17:02  dischi
# use normal button height as item height
#
# Revision 1.16  2003/06/02 03:28:41  rshortt
# Fixes for event changes.
#
# Revision 1.15  2003/05/27 17:53:34  dischi
# Added new event handler module
#
# Revision 1.14  2003/05/21 00:04:26  rshortt
# General improvements to layout and drawing.
#
# Revision 1.13  2003/05/15 02:21:54  rshortt
# got RegionScroller, ListBox, ListItem, OptionBox working again, although
# they suffer from the same label alignment bouncing bug as everything else
#
# Revision 1.12  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.11  2003/04/24 19:56:23  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.10  2003/04/20 13:02:29  dischi
# make the rc changes here, too
#
# Revision 1.9  2003/03/30 20:50:00  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.8  2003/03/30 18:19:53  rshortt
# Adding self to the other GetPopupBoxStyle calls.
#
# Revision 1.5  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
#
# Revision 1.4  2003/03/05 03:53:34  rshortt
# More work hooking skin properties into the GUI objects, and also making
# better use of OOP.
#
# ListBox and others are working again, although I have a nasty bug regarding
# alpha transparencies and the new skin.
#
# Revision 1.2  2003/02/23 18:30:45  rshortt
# Fixed a really annoying bug where items got reused and appended to.
# I have about a zillion lines of debug print statements to remove. :)
# Thanks to Krister for the help nailing it.
#
# Revision 1.1  2003/02/23 18:24:04  rshortt
# New classes.  ListBox is a subclass of RegionScroller so that it can
# scroll though a list of ListItems which are drawn to a surface.
# Also included is a listboxdemo to demonstrate and test everything.
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
from Button         import *
from Label          import * 
from ListItem       import * 
from types          import * 
import pygame

DEBUG = 0


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


        dummy_surface = pygame.Surface((1,1), 0, 32)

        RegionScroller.__init__(self, dummy_surface, left, top, width, 
                                height, bg_color, fg_color,
                                border, bd_color, bd_width,
                                self.show_h_scrollbar, self.show_v_scrollbar)

        self.set_surface(pygame.Surface(self.get_size(), 0, 32))

        self.h_margin                 = 2
        self.v_margin                 = 2
        self.items_height             = Button('foo').height
        self.x_scroll_interval        = 25
        self.y_scroll_interval        = self.items_height
        if not self.items: self.items = []

        if self.items: self.set_items(self.items)


    def scroll(self, direction):
        if DEBUG: print 'listbox scroll: direction="%s"' % direction

        if direction in (em.INPUT_RIGHT, em.INPUT_LEFT):
            return RegionScroller.scroll(self, direction)

        elif direction == em.INPUT_DOWN:

            i = self.get_selected_index()
            if i < len(self.items)-1:
                self.toggle_selected_index(i)
                self.toggle_selected_index(i+1)

                # if we are all the way down
                new_select = self.get_selected_item()
                if new_select.top + new_select.height > self.v_y + self.height:
                    return RegionScroller.scroll(self, direction)

        elif direction == em.INPUT_UP:

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
        self.set_surface(pygame.Surface((x, y), 0, 32))
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
            # item.draw(self.region_surface)
            item.draw()

        RegionScroller._draw(self, surface)


    def destroy(self):
        for item in self.items:
            item.destroy()
            item = None
        self.items = []
        RegionScroller.destroy(self)


    def eventhandler(self, event):
        if DEBUG: print 'ListBox::eventhandler: event=%s' % event

        if event in (em.INPUT_UP, em.INPUT_DOWN, em.INPUT_LEFT, em.INPUT_RIGHT ):
            if DEBUG: print 'ListBox::eventhandler: should scroll' 
            self.scroll(event)
            self.parent.draw()
            self.osd.update(self.parent.get_rect())
            return
        else:
            return self.parent.eventhandler(event)


