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
# Revision 1.2  2003/04/24 19:56:26  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.1  2003/03/30 17:21:20  rshortt
# New classes: PasswordInputBox, PasswordLetterBox.
# PasswordLetterBox is a subclass of Letterbox, PasswordInputBox does not
# extend InputBox but instead is also a subclass of PopupBox.  LetterBoxGroup
# has a new constructor argument called 'type' which when set to 'password'
# will make a LetterBoxGroup of PasswordLetterBox's rather than Letterbox's.
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
        

    def __init__(self, text=" ", left=None, top=None, width=25, height=25, 
                 bg_color=None, fg_color=None, selected_color=None,
                 selected_bg_color=None, selected_fg_color=None,
                 border=None, bd_color=None, bd_width=None):

        LetterBox.__init__(self, text, left, top, width, height, bg_color, 
                           fg_color, selected_color, selected_bg_color, 
                           selected_fg_color, border, bd_color, bd_width)

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


    def _draw(self):
        """
        The actual internal draw function.

        """
        if not self.width or not self.height or not self.text:
            raise TypeError, 'Not all needed variables set.'

        if self.selected:
            c = self.selected_bg_color.get_color_sdl()
            a = self.selected_bg_color.get_alpha()
        else:
            c = self.bg_color.get_color_sdl()
            a = self.bg_color.get_alpha()

        box = pygame.Surface(self.get_size(), 0, 32)
        box.fill(c)
        box.set_alpha(a)

        self.osd.screen.blit(box, self.get_position())

        if self.selected:
            self.selected_label.draw()
        else:
            self.label.draw()

        if self.border: self.border.draw()

    
    def get_text(self):
        return self.text

        
    def set_text(self, text):

        if DEBUG: print "Text: ", text
        if type(text) is StringType:
            self.text = text
        else:
            raise TypeError, type(text)

        self.real_char = text
        if text != ' ':
            text = '*'

        if not self.label:
            self.label = Label(text)
            self.label.set_parent(self)
            # XXX Set the background color to none so it is transparent.
            self.label.set_background_color(None)
            self.label.set_h_margin(self.h_margin)
            self.label.set_v_margin(self.v_margin)
        else:
            self.label.set_text(text)

        if not self.selected_label:
            self.selected_label = Label(text)
            self.selected_label.set_parent(self)
            # XXX Set the background color to none so it is transparent.
            self.selected_label.set_background_color(None)
            self.selected_label.set_h_margin(self.h_margin)
            self.selected_label.set_v_margin(self.v_margin)
        else:
            self.selected_label.set_text(text)

        self.label.set_v_align(Align.MIDDLE)
        self.label.set_h_align(Align.CENTER)
        self.selected_label.set_v_align(Align.MIDDLE)
        self.selected_label.set_h_align(Align.CENTER)


    def get_font(self):
        """
        Does not return OSD.Font object, but the filename and size as list.
        """
        return (self.label.font.filename, self.label.font.ptsize)


    def set_font(self, label, file, size, color):
        """
        Set the font.

        Just hands the info down to the label. Might raise an exception.
        """
        label.set_font(file, size, color)


    def set_border(self, bs):
        """
        bs  Border style to create.
        
        Set which style to draw border around object in. If bs is 'None'
        no border is drawn.
        
        Default is to have no border.
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


