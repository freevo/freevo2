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
# Revision 1.15  2004/02/21 19:33:24  dischi
# enhance input box, merge password and normal input
#
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

from GUIObject       import Align
from Container       import Container
from LayoutManagers  import LayoutManager
from Button          import Button
from event           import *

class LetterBoxGroup(Container):
    """
    x         x coordinate. Integer
    y         y coordinate. Integer
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
                 x=None, y=None, width=None, height=None, bg_color=None, 
                 fg_color=None, selected_bg_color=None, selected_fg_color=None,
                 border=None, bd_color=None, bd_width=None):

        Container.__init__(self, 'widget', x, y, width, height, bg_color,
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
            lb = LetterBox(border=None)
            if self.type != 'password': 
                if self.text and len(self.text) > i:
                    lb.set_text(self.text[i])

            l = l + lb.width - self.bd_width
            if lb.height > h:  h = lb.height
            if i == 0:
                lb.toggle_selected()
            self.add_child(lb)
            self.boxes.append(lb)

        self.width  = l + self.bd_width
        self.height = h

        self.set_h_align(Align.CENTER)
        self.last_key = None


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
            if hasattr(box, 'real_text'):
                word += box.real_text
            else:
                word = word + box.get_text()
        return word.rstrip()


    def _draw(self):
        """
        The actual internal draw function.
        """
        self.surface = self.get_surface()
        Container._draw(self)


    def eventhandler(self, event):
        """
        Handle basic events for this widget. Returns True when the event
        was used and a redraw is needed.
        """
        if self.type == 'password': 
            if event == INPUT_LEFT or event == INPUT_UP:
                the_box = self.get_selected_box()
                if self.boxes.index(the_box) != 0:
                    self.change_selected_box('left')
                    the_box = self.get_selected_box()
                    the_box.set_text(' ')
                    the_box.real_text = ''
                return True

            if event in INPUT_ALL_NUMBERS:
                the_box = self.get_selected_box()
                the_box.real_text = str(event.arg)
                the_box.set_text('*')
                if self.boxes.index(the_box) != len(self.boxes)-1:
                    self.change_selected_box('right')
                return True
            
        else:
            if event == INPUT_LEFT:
                self.change_selected_box('left')
                self.last_key = None
                return True

            if event == INPUT_RIGHT:
                self.change_selected_box('right')
                self.last_key = None
                return True

            if event == INPUT_UP:
                self.get_selected_box().charUp()
                self.last_key = None
                return True

            if event == INPUT_DOWN:
                self.get_selected_box().charDown()
                self.last_key = None
                return True

            if event in INPUT_ALL_NUMBERS:
                if self.last_key and self.last_key != event:
                    self.change_selected_box('right')
                self.last_key = event
                self.get_selected_box().cycle_phone_char(event.arg)
                return True

        return False


    
class LetterBox(Button):
    """
    x         x coordinate. Integer
    y         y coordinate. Integer
    width     Integer
    height    Integer
    text      Letter to hold.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """
    ourChars = [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 
                 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 
                 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 
                 '-', '.', ' ' ] 

    phoneChars = ([ " ", "-", ".", "0" ],
                  [ "1", ],
                  [ "A", "B", "C", "2" ],
                  [ "D", "E", "F", "3" ],
                  [ "G", "H", "I", "4" ],
                  [ "J", "K", "L", "5" ],
                  [ "M", "N", "O", "6" ],
                  [ "P", "Q", "R", "S", "7" ],
                  [ "T", "U", "V"  "8"],
                  [ "W", "X", "Y", "Z" ,"9"])
        

    def __init__(self, text=' ', x=None, y=None, width=35, height=35, 
                 bg_color=None, fg_color=None, selected_bg_color=None, 
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None):

        Button.__init__(self, text, None, x, y, width, height, bg_color,
                        fg_color, selected_bg_color, selected_fg_color,
                        border, bd_color, bd_width)

        self.h_margin  = 0
        self.v_margin  = 0
        self.h_spacing = 0
        self.v_spacing = 0
        self.set_v_align(Align.BOTTOM)
        self.set_h_align(Align.CENTER)
        self.label.set_v_align(Align.CENTER)
        self.label.set_h_align(Align.CENTER)


    def set_text(self, text):
        text = text.upper()
        Button.set_text(self, text)
        self.label.width  = self.width
        self.label.height = self.height
        self.label.set_v_align(Align.CENTER)
        self.label.set_h_align(Align.CENTER)


    def charUp(self):
        charNow = self.ourChars.index(self.text)
        if charNow < len(self.ourChars)-1:
            charNext = charNow + 1
        else:
            charNext = 0

        self.set_text(self.ourChars[charNext])


    def charDown(self):
        charNow = self.ourChars.index(self.text)
        if charNow > 0:
            charNext = charNow - 1
        else:
            charNext = len(self.ourChars)-1

        self.set_text(self.ourChars[charNext])


    def cycle_phone_char(self, number):
        letters = self.phoneChars[number]

        if not self.text in letters:
            self.set_text(letters[0])
        else:
            i = letters.index(self.text)
            if i < len(letters)-1:
                i = i + 1
            else:
                i = 0
            self.set_text(letters[i])


class LetterBoxLayout(LayoutManager):

    def __init__(self, container):
        self.container = container


    def layout(self):
        y = l = 0
        for box in self.container.boxes:
            x = l
            l = l + box.width - self.container.bd_width
            box.set_position(x, y)

