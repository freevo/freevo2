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
# Revision 1.15  2003/09/13 10:32:55  dischi
# fix a font problem and cleanup some unneeded stuff
#
# Revision 1.14  2003/09/06 13:59:19  gsbarbieri
# Now buttons try to get height from font if no value was given as argument.
#
# Revision 1.13  2003/09/05 15:59:20  outlyer
# Use StringTypes instead of "StringType" since StringTypes includes unicode,
# which TV listings are sometimes in (like mine)
#
# The change to the StringTypes tuple has existed since Python 2.2 (at least)
# so it should be fine.
#
# This prevents massive explosions on mine.
#
# Revision 1.12  2003/06/25 02:27:39  rshortt
# Allow 'frame' containers to grow verticly to hold all contents.  Also
# better control of object's background images.
#
# Revision 1.11  2003/05/27 17:53:34  dischi
# Added new event handler module
#
# Revision 1.10  2003/05/21 00:04:25  rshortt
# General improvements to layout and drawing.
#
# Revision 1.9  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.8  2003/04/24 19:56:18  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.7  2003/03/30 20:49:59  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.6  2003/03/30 18:19:53  rshortt
# Adding self to the other GetPopupBoxStyle calls.
#
# Revision 1.5  2003/03/23 23:19:39  rshortt
# When selected these objects now use skin properties as well.
#
# Revision 1.4  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
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
import skin

from GUIObject  import *
from Container  import *
from Color      import *
from Border     import *
from Label      import * 
from types      import * 

DEBUG = 0


class Button(Container):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      The label on the button. String
    handler   Function to call when button is hit
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    selected_bg_color  Background color (Color)
    selected_fg_color  Foreground color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    
    def __init__(self, text=' ', handler=None, left=None, top=None, 
                 width=70, height=None, bg_color=None, fg_color=None, 
                 selected_bg_color=None, selected_fg_color=None,
                 border=None, bd_color=None, bd_width=None):

        default_button_height = 25

        if not height:
            height = default_button_height

        Container.__init__(self, 'widget', left, top, width, height, bg_color,
                           fg_color, selected_bg_color, selected_fg_color,
                           border, bd_color, bd_width)

        self.h_margin          = 2
        self.v_margin          = 2

        if not height:
            if self.skin_info_widget.font:
                nf = OSDFont( self.skin_info_widget.font.name,
                              self.skin_info_widget.font.size )
                height = nf.height

            if self.skin_info_widget_selected.font:
                sf = OSDFont( self.skin_info_widget_selected.font.name, \
                              self.skin_info_widget_selected.font.size )
                if height:
                    height = max( height, sf.height)
                else:
                    height = sf.height
                
            if not height:
                height = default_button_height

            self.height = height

        self.handler           = handler

        if type(text) in StringTypes:
            if text: self.set_text(text)
        elif not text:
            self.text = None
        else:
            raise TypeError, text


        if self.skin_info_widget.font:       
            font_size_setting = self.skin_info_widget.font.size
            font_percent = font_size_setting * 100 / default_button_height 
            font_size = int(font_percent * self.height / 120) # cheat smaller
            self.set_font(self.label, 'normal',
                          self.skin_info_widget.font.name, 
                          font_size, 
                          self.fg_color)
        else:
            self.set_font(config.OSD_DEFAULT_FONTNAME,
                          config.OSD_DEFAULT_FONTSIZE)

        if self.skin_info_widget_selected.font:       
            font_size_setting = self.skin_info_widget.font.size
            font_percent = font_size_setting * 100 / default_button_height 
            font_size = int(font_percent * self.height / 120) # cheat smaller
            self.set_font(self.label, 'selected',
                          self.skin_info_widget_selected.font.name, 
                          font_size, 
                          self.selected_fg_color)
        else:
            self.set_font(self.selected_label,
                          config.OSD_DEFAULT_FONTNAME,
                          config.OSD_DEFAULT_FONTSIZE)

        # now check the height, maybe the font is too large
        self.height = max(self.height, self.label.font.height + 2 * self.v_margin)

        self.set_v_align(Align.BOTTOM)
        self.set_h_align(Align.CENTER)


    def _draw(self):
        if not self.width or not self.height or not self.text:
            raise TypeError, 'Not all needed variables set.'

        if self.selected:
            c = self.selected_bg_color.get_color_sdl()
            a = self.selected_bg_color.get_alpha()
        else:
            c = self.bg_color.get_color_sdl()
            a = self.bg_color.get_alpha()

        self.surface = pygame.Surface(self.get_size(), 0, 32)
        self.surface.fill(c)
        self.surface.set_alpha(a)

        Container._draw(self)

        self.blit_parent()

    
    def get_text(self):
        return self.text

        
    def set_text(self, text):

        if DEBUG: print "Button::set_text: text=%s" % text
        if type(text) in StringTypes:
            self.text = text
        else:
            raise TypeError, type(text)

        if not self.label:
            self.label = Label()
            self.label.set_text(text)
            self.label.set_background_color(None)
            self.add_child(self.label)
        else:
            self.label.set_text(text)

        self.label.set_v_align(Align.CENTER)
        self.label.set_h_align(Align.CENTER)

        self.surface_changed = 1


    def get_font(self):
        """
        Does not return OSD.Font object, but the filename and size as list.
        """
        return (self.label.font.name, self.label.font.ptsize)


    def set_font(self, label, state, file, size, color):
        """
        Set the font.

        Just hands the info down to the label. Might raise an exception.
        """
        label.set_font(state, file, size, color)


    def eventhandler(self, event):
        return self.parent.eventhandler(event)


