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
# Revision 1.12  2003/06/25 02:27:39  rshortt
# Allow 'frame' containers to grow verticly to hold all contents.  Also
# better control of object's background images.
#
# Revision 1.11  2003/05/21 00:04:26  rshortt
# General improvements to layout and drawing.
#
# Revision 1.10  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.9  2003/04/24 19:56:22  dischi
# comment cleanup for 1.3.2-pre4
#
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

from Container          import Container
from LayoutManagers     import LayoutManager
from LetterBox          import * 
from PasswordLetterBox  import * 

DEBUG = 0


class LetterBoxGroup(Container):
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
                 fg_color=None, selected_bg_color=None, selected_fg_color=None,
                 border=None, bd_color=None, bd_width=None):

        Container.__init__(self, 'widget', left, top, width, height, bg_color,
                           fg_color, selected_bg_color, selected_fg_color,
                           border, bd_color, bd_width)

        self.h_margin  = 0
        self.v_margin  = 0
        self.h_spacing = 0
        self.v_spacing = 0

        self.text     = text
        self.type     = type
        self.numboxes = numboxes
        self.boxes    = []

        self.set_layout(LetterBoxLayout(self))

        l = 0
        h = 0
        for i in range(self.numboxes):
            if self.type == 'password': 
                lb = PasswordLetterBox()
            else:
                lb = LetterBox()
                if self.text and len(self.text) > i:
                    lb.set_text(self.text[i])

            l = l + lb.width
            if lb.height > h:  h = lb.height
            if i == 0:
                lb.toggle_selected()
            self.add_child(lb)
            self.boxes.append(lb)

        self.width = l
        self.height = h

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
            if isinstance(box, PasswordLetterBox):
                word += box.real_char
            else:
                word = word + box.get_text()

        return word.rstrip()


    def _draw(self):
        """
        The actual internal draw function.

        """
        self.surface = self.parent.surface.subsurface((self.left,
                                                       self.top,
                                                       self.width,
                                                       self.height))

        Container._draw(self)

        self.blit_parent()

    
class LetterBoxLayout(LayoutManager):

    def __init__(self, container):
        self.container = container


    def layout(self):
        top = l = 0
        for box in self.container.boxes:
            left = l
            l = l + box.width
            box.set_position(left, top)

