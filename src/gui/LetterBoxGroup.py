#if 0 /*
# -----------------------------------------------------------------------
# LetterBoxGroup.py - a class that combines LetterBox's so the user
#                     can input words.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
#
# Revision 1.2  2003/03/05 03:53:34  rshortt
# More work hooking skin properties into the GUI objects, and also making
# better use of OOP.
#
# ListBox and others are working again, although I have a nasty bug regarding
# alpha transparencies and the new skin.
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

from GUIObject  import *
from Color      import *
from Border     import *
from Label      import * 
from LetterBox  import * 
from types      import * 
from osd import Font

DEBUG = 0


class LetterBoxGroup(GUIObject):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    handler   Function to call when ENTER is hit
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    
    def __init__(self, numboxes=7, text=None, handler=None, left=None, top=None, 
                 width=None, height=None, bg_color=None, fg_color=None, 
                 border=None, bd_color=None, bd_width=None):

        GUIObject.__init__(self)

        self.text     = text
        self.handler  = handler
        self.border   = border
        self.label    = None
        self.bd_color = bd_color
        self.bd_width = bd_width
        self.width    = width
        self.height   = height
        self.left     = left
        self.top      = top
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.h_margin = 2
        self.v_margin = 2
        self.numboxes = numboxes
        self.boxes    = []

        # XXX: Place a call to the skin object here then set the defaults
        #      acodringly. self.skin is set in the superclass.

        if not self.width:    self.width  = 1
        if not self.height:   self.height = 1
        if not self.left:     self.left   = -100
        if not self.top:      self.top    = -100
        if not self.bg_color: self.bg_color = Color(self.osd.default_bg_color)
        if not self.fg_color: self.fg_color = Color(self.osd.default_fg_color)
        if not self.bd_color: self.bd_color = Color(self.osd.default_fg_color) 
        if not self.bd_width: self.bd_width = 2
        if not self.border:   self.border = Border(self, Border.BORDER_FLAT, 
                                                   self.bd_color, self.bd_width)

        self.set_h_align(Align.CENTER)

        l = 0
        h = 0
        for i in range(self.numboxes):
            lb = LetterBox()
            top = self.top
            left = self.left + l
            l = l + lb.width
            if lb.height > h:  h = lb.height
            if i == 0:
                lb.toggle_selected()
            self.add_child(lb)
            self.boxes.append(lb)

        self.width = l
        self.height = h


    def get_selected_box(self):
        for box in self.boxes:
            if box.selected == 1:
                return box


    def change_selected_box(self, dir=None):
        boxNow = self.boxes.index(self.get_selected_box())

        if not dir:
            dir = 'right'

        if dir == 'right':
            if boxNow < len(self.boxes)-1:
                boxNext = boxNow + 1
            else:
                boxNext = 0
        else:
            if boxNow > 0:
                boxNext = boxNow - 1
            else:
                boxNext = len(self.boxes)-1

        self.boxes[boxNow].toggle_selected()
        self.boxes[boxNow].draw()
        self.boxes[boxNext].toggle_selected()
        self.boxes[boxNext].draw()


    def get_word(self):
        word = ''
        for box in self.boxes:
            word = word + box.get_text()

        return word


    def _draw(self):
        """
        The actual internal draw function.

        """
        if not self.width or not self.height:
            raise TypeError, 'Not all needed variables set.'

        if self.selected:
            c = self.selected_color.get_color_sdl()
            a = self.selected_color.get_alpha()
        else:
            c = self.bg_color.get_color_sdl()
            a = self.bg_color.get_alpha()

        box = pygame.Surface(self.get_size(), 0, 32)
        box.fill(c)
        box.set_alpha(a)

        self.osd.screen.blit(box, self.get_position())

        if self.border: self.border.draw()
        for box in self.boxes:
            box.draw()

    
    def set_border(self, bs):
        """
        bs  Border style to create.
        
        Set which style to draw border around object in. If bs is 'None'
        no border is drawn.
        
        Default for PopubBox is to have no border.
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

        l = 0
        for box in self.boxes:
            left = self.left + l
            l = l + box.width
            box.set_position(left, top)

        
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


