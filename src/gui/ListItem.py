#if 0 /*
# -----------------------------------------------------------------------
# ListItem.py - the primary component of a ListBox
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2003/05/15 02:21:54  rshortt
# got RegionScroller, ListBox, ListItem, OptionBox working again, although
# they suffer from the same label alignment bouncing bug as everything else
#
# Revision 1.8  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.7  2003/04/24 19:56:24  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.6  2003/03/30 20:50:00  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.5  2003/03/30 18:19:53  rshortt
# Adding self to the other GetPopupBoxStyle calls.
#
# Revision 1.4  2003/03/23 23:19:39  rshortt
# When selected these objects now use skin properties as well.
#
# Revision 1.3  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
#
# Revision 1.2  2003/02/24 11:58:28  rshortt
# Adding OptionBox and optiondemo.  Also some minor cleaning in a few other
# objects.
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

from GUIObject import *
from Color     import *
from Border    import *
from Button    import *
from Label     import * 
from types     import * 
from osd import Font

DEBUG = 0


class ListItem(Button):
    """
    width     Integer
    height    Integer
    text      Letter to hold.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    
    def __init__(self, text=' ', value=None, width=75, height=25, 
                 bg_color=None, fg_color=None, selected_bg_color=None,
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None):

        handler = None
        left = 0
        top = 0

        Button.__init__(self, text, handler, left, top, width, height, bg_color,
                        fg_color, selected_bg_color, selected_fg_color,
                        border, bd_color, bd_width)

        self.value             = value
        self.h_margin          = 20
        self.v_margin          = 2
        self.label.set_v_align(Align.CENTER)
        self.label.set_h_align(Align.LEFT)


    def _draw(self, surface=None):
#        """
#        The actual internal draw function.
#
#        """
#        if not self.width or not self.height or not self.text:
#            raise TypeError, 'Not all needed variables set.'
#
#        if not surface:
#            surface = self.parent.surface
#
#        if self.selected:
#            c = self.selected_bg_color.get_color_sdl()
#            a = self.selected_bg_color.get_alpha()
#        else:
#            c = self.bg_color.get_color_sdl()
#            a = self.bg_color.get_alpha()
#
#        box = pygame.Surface(self.get_size(), 0, 32)
#        box.fill(c)
#        box.set_alpha(a)
#
#        if surface:
#            surface.blit(box, self.get_position())
#        else:
#            self.osd.screen.blit(box, self.get_position())
#
#        if self.selected:
#            self.selected_label.draw(surface)
#        else:
#            self.label.draw(surface)
#
#        if self.border: self.border.draw(surface)

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

        Container._draw(self)

        self.parent.region_surface.blit(self.surface, self.get_position())


    
