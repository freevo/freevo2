#if 0 /*
# -----------------------------------------------------------------------
# PasswordLetterBox.py - a gui widget for inputting a password character
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2004/02/18 21:52:04  dischi
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
# Revision 1.5  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.4  2003/09/13 10:32:56  dischi
# fix a font problem and cleanup some unneeded stuff
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

from GUIObject  import *
from LetterBox  import * 


class PasswordLetterBox(LetterBox):
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

    
    phoneChars = {
        1 : ["1"],
        2 : ["2"],
        3 : ["3"],
        4 : ["4"],
        5 : ["5"],
        6 : ["6"],
        7 : ["7"],
        8 : ["8"],
        9 : ["9"],
        0 : ["0"],
    }
        

    def __init__(self, text=" ", left=None, top=None, width=35, height=35, 
                 bg_color=None, fg_color=None, selected_bg_color=None, 
                 selected_fg_color=None, border=None, bd_color=None, 
                 bd_width=None):

        LetterBox.__init__(self, text, left, top, width, height, bg_color, 
                           fg_color,selected_bg_color, selected_fg_color, 
                           border, bd_color, bd_width)

        self.real_char = ' '


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


    def set_text(self, text):

        self.real_char = text
        if text != ' ':
            text = '*'

        LetterBox.set_text(self, text)


