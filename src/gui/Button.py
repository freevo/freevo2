#if 0 /*
# -----------------------------------------------------------------------
# Button.py - a simple button class
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/02/18 13:40:52  rshortt
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
from types      import * 
from osd import Font

DEBUG = 1


class Button(GUIObject):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      The label on the button. String
    handler   Function to call when button is hit
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    
    def __init__(self, text, handler=None, icon=None, left=None, top=None, 
                 width=None, height=None, bg_color=None, fg_color=None, 
                 selected_color=None, border=None, bd_color=None, 
                 bd_width=None):

        GUIObject.__init__(self)

        self.text           = text
        self.handler        = handler
        self.icon           = icon
        self.border         = border
        self.label          = None
        self.h_margin       = 10
        self.v_margin       = 10
        self.bd_color       = bd_color
        self.bd_width       = bd_width
        self.width          = width
        self.height         = height
        self.left           = left
        self.top            = top
        self.bg_color       = bg_color
        self.fg_color       = fg_color
        self.selected_color = selected_color

        # XXX: Place a call to the skin object here then set the defaults
        #      acodringly. self.skin is set in the superclass.

        if not self.width:    self.width    = 70
        if not self.height:   self.height   = 25
        if not self.left:     self.left     = -100
        if not self.top:      self.top      = -100
        if not self.bg_color: self.bg_color = Color(self.osd.default_bg_color)
        if not self.fg_color: self.fg_color = Color(self.osd.default_fg_color)
        if not self.bd_color: self.bd_color = Color(self.osd.default_fg_color) 
        if not self.bd_width: self.bd_width = 2
        if not self.border:   self.border   = Border(self, Border.BORDER_FLAT, 
                                                     self.bd_color, self.bd_width)

        if not self.selected_color: self.selected_color = Color((0,255,0,128))

        self.set_v_align(Align.BOTTOM)
        self.set_h_align(Align.CENTER)

        if type(text) is StringType:
            if text: self.set_text(text)
        elif not text:
            self.text = None
        else:
            raise TypeError, text


    def _draw(self):
        if not self.width or not self.height or not self.text:
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

        if self.label:  self.label._draw()
        if self.border: self.border._draw()

    
    def get_text(self):
        return self.text

        
    def set_text(self, text):

        if DEBUG: print "Text: ", text
        if type(text) is StringType:
            self.text = text
        else:
            raise TypeError, type(text)

        if not self.label:
            self.label = Label(text)
            self.label.set_parent(self)
            # These values can also be maipulated by the user through
            # get_font and set_font functions.
            self.label.set_font( config.OSD_DEFAULT_FONTNAME,
                                 config.OSD_DEFAULT_FONTSIZE )
            # XXX Set the background color to none so it is transparent.
            self.label.set_background_color(None)
            self.label.set_h_margin(self.h_margin)
            self.label.set_v_margin(self.v_margin)
            self.label.set_h_align(Align.CENTER)
        else:
            self.label.set_text(text)

        self.label.set_v_align(Align.MIDDLE)
        self.label.set_h_align(Align.CENTER)


    def get_font(self):
        """
        Does not return OSD.Font object, but the filename and size as list.
        """
        return (self.label.font.filename, self.label.font.ptsize)


    def set_font(self, file, size):
        """
        Set the font.

        Just hands the info down to the label. Might raise an exception.
        """
        if self.label:
            self.label.set_font(file, size)
        else:
            raise TypeError, file


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


    def eventhandler(self, event):
            return self.parent.eventhandler(event)



