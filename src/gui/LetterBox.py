#if 0 /*
# -----------------------------------------------------------------------
# LetterBox.py - a gui widget for inputting a letter
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.15  2004/02/18 21:52:04  dischi
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
# Revision 1.14  2004/01/09 02:08:07  rshortt
# GUI fixes from Matthieu Weber.
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

import string
import config
from event import *

from GUIObject import Align
from Button import Button


class LetterBox(Button):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
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

    phoneChars = {
        INPUT_1.name : ["1"],
        INPUT_2.name : ["2", "A", "B", "C"],
        INPUT_3.name : ["3", "D", "E", "F"],
        INPUT_4.name : ["4", "G", "H", "I"],
        INPUT_5.name : ["5", "J", "K", "L"],
        INPUT_6.name : ["6", "M", "N", "O"],
        INPUT_7.name : ["7", "P", "Q", "R", "S"],
        INPUT_8.name : ["8", "T", "U", "V"],
        INPUT_9.name : ["9", "W", "X", "Y", "Z"],
        INPUT_0.name : ["0", "-", ".", " "],
    }
        

    def __init__(self, text=' ', left=None, top=None, width=35, height=35, 
                 bg_color=None, fg_color=None, selected_bg_color=None, 
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None):

        handler = None

        Button.__init__(self, text, handler, left, top, width, height, bg_color,
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
        text = string.upper(text)
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


    def cycle_phone_char(self, command):
        command = int(command)

        if not self.phoneChars.has_key(command):
            return

        letters = self.phoneChars[command]

        if letters.count(self.text) <= 0:
            self.set_text(letters[0])
        else:
            i = letters.index(self.text)
            if i < len(letters)-1:
                i = i + 1
            else:
                i = 0
            self.set_text(letters[i])
