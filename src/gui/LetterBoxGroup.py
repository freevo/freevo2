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
# Revision 1.8  2003/03/30 20:50:00  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.7  2003/03/30 18:19:53  rshortt
# Adding self to the other GetPopupBoxStyle calls.
#
# Revision 1.6  2003/03/30 17:21:19  rshortt
# New classes: PasswordInputBox, PasswordLetterBox.
# PasswordLetterBox is a subclass of Letterbox, PasswordInputBox does not
# extend InputBox but instead is also a subclass of PopupBox.  LetterBoxGroup
# has a new constructor argument called 'type' which when set to 'password'
# will make a LetterBoxGroup of PasswordLetterBox's rather than Letterbox's.
#
# Revision 1.5  2003/03/30 16:15:42  rshortt
# Got rid of trailing whitespaces from the 'word'.
#
# Revision 1.4  2003/03/24 02:40:50  rshortt
# These objects are now using skin properties.
#
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

from GUIObject          import *
from Color              import *
from Border             import *
from Label              import * 
from LetterBox          import * 
from PasswordLetterBox  import * 
from types              import * 
from osd import         Font

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

    
    def __init__(self, numboxes=7, text=None, handler=None, type=None, 
                 left=None, top=None, width=None, height=None, bg_color=None, 
                 fg_color=None, border=None, bd_color=None, bd_width=None):

        GUIObject.__init__(self, left, top, width, height)

        # XXX: text not supported yet
        self.text     = text
        self.handler  = handler
        self.type     = type
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border   = border
        self.bd_color = bd_color
        self.bd_width = bd_width
        self.numboxes = numboxes
        self.boxes    = []


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

        if not self.bd_width: 
            if self.skin_info_widget.rectangle.size:
                self.bd_width = self.skin_info_widget.rectangle.size
            else:
                self.bd_width = 1

        l = 0
        h = 0
        for i in range(self.numboxes):
            if self.type == 'password': 
                lb = PasswordLetterBox()
            else:
                lb = LetterBox()
            l = l + lb.width
            if lb.height > h:  h = lb.height
            if i == 0:
                lb.toggle_selected()
            self.add_child(lb)
            self.boxes.append(lb)

        self.width = l
        self.height = h

        if not self.border:   
            self.border = Border(self, Border.BORDER_FLAT,
                                 self.bd_color, self.bd_width)

        self.set_h_align(Align.CENTER)


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
            if isinstance(self.border, PasswordLetterBox):
                word += box.real_char
            else:
                word = word + box.get_text()

        return word.rstrip()


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


