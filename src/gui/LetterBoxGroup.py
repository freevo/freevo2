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
# Revision 1.14  2004/02/18 21:52:04  dischi
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
# Revision 1.13  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.12  2003/06/25 02:27:39  rshortt
# Allow 'frame' containers to grow verticly to hold all contents.  Also
# better control of object's background images.
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

import config

from Container          import Container
from LayoutManagers     import LayoutManager
from LetterBox          import * 
from PasswordLetterBox  import * 


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
        self.boxes[boxNext].toggle_selected()


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
        self.surface = self.get_surface()
        Container._draw(self)

    
class LetterBoxLayout(LayoutManager):

    def __init__(self, container):
        self.container = container


    def layout(self):
        top = l = 0
        for box in self.container.boxes:
            left = l
            l = l + box.width
            box.set_position(left, top)

