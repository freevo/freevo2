# -*- coding: iso-8859-1 -*-
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
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.18  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.17  2004/04/25 18:19:10  mikeruelle
# missing comma causes 8 to not show
#
# Revision 1.16  2004/03/13 22:32:44  dischi
# Improve input handling:
# o support upper and lower case
# o variable box width up to a length of 60 chars
# o keyboard input
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
import copy

from GUIObject       import Align
from Container       import Container
from LayoutManagers  import LayoutManager
from Button          import Button
from Border          import Border
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

        self.h_margin  = 5
        self.v_margin  = 0
        self.h_spacing = 0
        self.v_spacing = 0

        self.text     = text
        self.type     = type
        self.boxes    = []

        self.set_layout(LetterBoxLayout(self))

        bw = 0
        for c in ('M', 'A', 'm'):
            bw = max(bw, self.content_layout.types['button'].font.stringsize(c),
                     self.content_layout.types['button selected'].font.stringsize(c))

        bw += 2
        
        l = 0
        h = 0

        for i in range(numboxes or 60):
            lb = LetterBox(width=bw)

            if self.type != 'password': 
                if self.text and len(self.text) > i:
                    lb.set_text(self.text[i], fix_case=False)
                else:
                    lb.set_text(' ')
            l = l + lb.width
            h = max(lb.height, h)

            self.add_child(lb)
            if self.boxes:
                lb.upper_case = False
            self.boxes.append(lb)

        self.width  = min(self.width, l + self.bd_width + 2 * self.h_margin)
        self.height = h

        self.set_h_align(Align.CENTER)
        self.last_key = None
        
        if self.type != 'password' and self.text and len(self.text) < len(self.boxes):
            self.boxes[len(self.text)].toggle_selected()
        else:
            self.boxes[0].toggle_selected()


    def get_selected_box(self):
        for box in self.boxes:
            if box.selected == 1:
                return box


    def change_selected_box(self, dir='right', allow_roundtrip=False):
        boxNow  = self.boxes.index(self.get_selected_box())
        boxNext = boxNow

        if dir == 'right':
            if boxNow < len(self.boxes)-1:
                boxNext = boxNow + 1
                if self.boxes[boxNow].text == ' ':
                    self.boxes[boxNext].upper_case = True
                if not self.boxes[boxNext].visible and allow_roundtrip:
                    boxNext = 0
            elif allow_roundtrip:
                boxNext = 0
                
        else:
            if boxNow > 0:
                boxNext = boxNow - 1
            elif allow_roundtrip:
                for x in range(len(self.boxes)):
                    if self.boxes[x].visible:
                        boxNext = x

        if self.boxes[boxNext].visible and boxNext != boxNow:
            self.boxes[boxNow].toggle_selected()
            self.boxes[boxNext].toggle_selected()


    def get_word(self):
        word = ''
        for box in self.boxes:
            if box.visible:
                if hasattr(box, 'real_text'):
                    word += box.real_text
                else:
                    word = word + box.get_text()
        return word.rstrip()


    def set_word(self, text):
        for i in range(min(len(self.boxes), len(text))):
            self.boxes[i].set_text(text[i], fix_case=False)

            
    def _draw(self):
        """
        The actual internal draw function.
        """

        rect = self.content_layout.types['button'].rectangle
        self.surface = self.get_surface()
        self.osd.drawroundbox(0, 0, self.width, self.height, rect.bgcolor, 0, rect.color,
                              0, self.surface)
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
                self.change_selected_box('left', allow_roundtrip=True)
                self.last_key = None
                return True

            if event == INPUT_RIGHT:
                self.change_selected_box('right', allow_roundtrip=True)
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

            if event == BUTTON:
                # direct key input (I hope)
                self.get_selected_box().set_text(event.arg, fix_case=False)
                self.change_selected_box('right')
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
                  [ "T", "U", "V", "8"],
                  [ "W", "X", "Y", "Z" ,"9"])
        

    def __init__(self, text=' ', x=None, y=None, width=35, height=35, 
                 bg_color=None, fg_color=None, selected_bg_color=None, 
                 selected_fg_color=None):

        self.upper_case = True
        self.max_width  = width

        Button.__init__(self, text, None, x, y, width, height, bg_color,
                        fg_color, selected_bg_color, selected_fg_color, border=None)

        self.h_margin  = 0
        self.v_margin  = 0
        self.h_spacing = 0
        self.v_spacing = 0
        self.set_v_align(Align.BOTTOM)
        self.set_h_align(Align.CENTER)
        self.label.set_v_align(Align.CENTER)
        self.label.set_h_align(Align.CENTER)

        for c in copy.copy(self.children):
            if isinstance(c, Border):
                self.children.remove(c)

        self.border = -1
        

    def draw(self):
        if self.left + self.max_width <= self.parent.width - self.parent.bd_width - \
           2 * self.parent.h_margin:
            self.visible = True
        else:
            self.visible = False
        Button.draw(self)
        
        
    def set_text(self, text, fix_case=True):
        if fix_case:
            if self.upper_case:
                text = text.upper()
            else:
                text = text.lower()
        Button.set_text(self, text)
        self.label.set_v_align(Align.CENTER)
        self.label.set_h_align(Align.CENTER)
        if self.label.font:
            self.label.width = self.max_width
            self.width = self.label.get_rendered_size()[0] or self.max_width
            self.width += 4


    def charUp(self):
        try:
            charNow = self.ourChars.index(self.text.upper())
            if charNow < len(self.ourChars)-1:
                charNext = charNow + 1
            else:
                charNext = 0
        except:
            charNext = 0

        self.set_text(self.ourChars[charNext])


    def charDown(self):
        try:
            charNow = self.ourChars.index(self.text.upper())
            if charNow > 0:
                charNext = charNow - 1
            else:
                charNext = len(self.ourChars)-1
        except:
            charNext = 0

        self.set_text(self.ourChars[charNext])


    def cycle_phone_char(self, number):
        letters = self.phoneChars[number]

        if not self.text.upper() in letters:
            self.set_text(letters[0])
        else:
            i = letters.index(self.text.upper())
            if i < len(letters)-1:
                i = i + 1
            else:
                i = 0
                self.upper_case = not self.upper_case
            self.set_text(letters[i])



class LetterBoxLayout(LayoutManager):

    def __init__(self, container):
        self.container = container

    def layout(self):
        y = 0
        l = self.container.h_margin

        for box in self.container.boxes:
            x = l
            l = l + box.width
            box.set_position(x, y)
