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
# Revision 1.10  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.9  2003/04/24 19:56:21  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.8  2003/03/30 20:50:00  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.7  2003/03/30 18:19:53  rshortt
# Adding self to the other GetPopupBoxStyle calls.
#
# Revision 1.6  2003/03/30 17:21:17  rshortt
# New classes: PasswordInputBox, PasswordLetterBox.
# PasswordLetterBox is a subclass of Letterbox, PasswordInputBox does not
# extend InputBox but instead is also a subclass of PopupBox.  LetterBoxGroup
# has a new constructor argument called 'type' which when set to 'password'
# will make a LetterBoxGroup of PasswordLetterBox's rather than Letterbox's.
#
# Revision 1.5  2003/03/24 02:40:50  rshortt
# These objects are now using skin properties.
#
# Revision 1.4  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
#
# Revision 1.3  2003/03/07 00:19:58  rshortt
# Just a quick fix to take care of redrawing when changing the letter and still
# seeing the previous letter though the alpha.  I will have to come up with
# a better solution (probably using a bg_surface or something) when I hook
# this object up to the skin properties because if the non-selected bg_color
# has a transparency it will still be broken.
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

from GUIObject import Align
from Button import Button

DEBUG = 0


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
        1 : ["1"],
        2 : ["2", "A", "B", "C"],
        3 : ["3", "D", "E", "F"],
        4 : ["4", "G", "H", "I"],
        5 : ["5", "J", "K", "L"],
        6 : ["6", "M", "N", "O"],
        7 : ["7", "P", "Q", "R", "S"],
        8 : ["8", "T", "U", "V"],
        9 : ["9", "W", "X", "Y", "Z"],
        0 : ["0", "-", ".", " "],
    }
        

    def __init__(self, text=' ', left=None, top=None, width=35, height=35, 
                 bg_color=None, fg_color=None, selected_bg_color=None, 
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None):

        handler = None

        Button.__init__(self, text, handler, left, top, width, height, bg_color,
                        fg_color, selected_bg_color, selected_fg_color,
                        border, bd_color, bd_width)


        self.h_margin          = 0
        self.v_margin          = 0
        self.h_spacing          = 0
        self.v_spacing          = 0
        self.set_v_align(Align.BOTTOM)
        self.set_h_align(Align.CENTER)


    def set_text(self, text):
        Button.set_text(self, text)
        self.label.width = self.width
        self.label.height = self.height


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


