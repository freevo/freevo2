#!/usr/bin/env python
#-----------------------------------------------------------------------
# Label - A class for text labels
#-----------------------------------------------------------------------
# $Id$
#
# Todo: o Do check to see if font has changed on draw to let people
#         change font between updates.
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/02/23 18:21:50  rshortt
# Some code cleanup, better OOP, influenced by creating a subclass of RegionScroller called ListBox.
#
# Revision 1.2  2003/02/18 13:40:52  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
#
# Revision 1.1  2002/12/07 15:21:31  dischi
# moved subdir gui into src
#
# Revision 1.3  2002/09/21 10:06:47  dischi
# Make it work again, the last change was when we used osd_sdl.py
#
# Revision 1.2  2002/08/18 21:54:12  tfmalt
# o Added support for vertical and horizontal alignment of text.
# o Added handling of vertical and horizontal margins to parent object.
# o Rewrote the render function. Labels can now both be separate and
#   child objects.
#
# Revision 1.1  2002/08/15 22:45:42  tfmalt
# o Inital commit of Freevo GUI library. Files are put in directory 'gui'
#   under Freevo.
# o At the moment the following classes are implemented (but still under
#   development):
#     Border, Color, Label, GUIObject, PopupBox, ZIndexRenderer.
# o These classes are fully workable, any testing and feedback will be
#   appreciated.
#
#-----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------
"""
A class for text labels

Label can only be used as part of containers.
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


import pygame

from GUIObject import *
from osd import Font

DEBUG = 0


class Label(GUIObject):
    """
    text    String, text to display
    align   Integer, h_align of text. Label.CENTER, Label.RIGHT,
            Label, LEFT
    parent  GUIObject, Reference to object containing this label.
    
    Displays a single line of text. Really it maintains a surface with a
    rendered text. If text is updated text is rerendered and reblitted to
    the screen.

    Both text and align can be set using functions. If text is not set when
    draw is called an exception is raised.
    """
    
    def __init__(self, text=None, h_align=None, v_align=None, parent=None):
        self.h_align  = Align.LEFT
        self.v_align  = Align.MIDDLE
        self.text     = None
        self.font     = None # This is a OSD.Font object not pygame.
        self.surface  = None
        self.parent   = None
        self.v_margin = 0
        self.h_margin = 0
        
        GUIObject.__init__(self)

        if h_align: self.set_h_align(align)
        if v_align: self.set_v_align(align)
        if text:    self.set_text(text)

        self.set_foreground_color(Color( (0,0,0,255) ))


    def get_text(self):
        """
        Returns text.
        """
        return self.text


    def set_text(self, text):
        """
        Sets text.
        """
        if type(text) is StringType:
            if self.surface: self.surface = None
            self.text = text
        else:
            raise TypeError, type(text)


    def set_font(self, font=None, size=None):
        """
        font  String. Filename of font to use.
        size  Size in pixels to render font.
        
        Sets the font of label.
        Uses _getfont in osd, and the fontcache in osd.
        """
        if type(font) is StringType and type(size) is IntType:
            if self.surface: self.surface = None
            # self.font = self._get_osd_font(font, size)
            self.font = self.osd._getfont(font, size)
        else:
            raise TypeError, 'font'

            
    def get_font(self):
        """
        Returns the fontobject.

        We keep a copy of _this_ font object inside 
        """
        return self.font


    def _get_osd_font(self, filename, size):
        """
        filename  Filename of font
        size      Size of font in pixels.
        
        Small reimplement of OSD._getfont.

        This is just a temporary workaround since I wnat the whole OSD.Font
        object in osd not just the pygame.font.Font
        """
        for f in self.osd.fontcache:
            if f.filename == filename and f.ptsize == size:
                return f

        font       = pygame.font.Font(filename, size)
        f          = Font()
        f.filename = filename
        f.ptsize   = size
        f.font     = font

        self.osd.fontcache.append(f)
        return f


    def render(self):
        """
        Mainly an internal function. Frontend to the fonts own render
        function.
        """
        if not self.font: raise TypeError, 'Oops, no font.'
        if not self.text: raise TypeError, 'Oops, no text.'
        fgc = self.fg_color.get_color_sdl()
        # print 'LABEL: fgc="%s,%s,%s,%s"' % fgc
        # self.surface = self.font.font.render(self.text, 1, fgc)
        self.surface = self.font.render(self.text, 1, fgc)
        self.set_size(self.surface.get_size())
        self.set_position(self.calc_position())
        

    def _draw(self, surface=None):
        """
        Our default _draw function.

        Add handling to check if font, size or text has changed.
        """
        if not self.surface:
            # XXX Currently we don't use background color since that
            # XXX Should be transparent
            self.render()

        
        # print 'LABEL._draw: "%s" parent x,y=%s' % (self.text, self.parent.get_position())
        # print 'LABEL._draw: "%s" x,y=%s' % (self.text, self.get_position())
        # XXX Fix h_align and stuff.
        if surface:
            surface.blit(self.surface, self.get_position())
        else:
            self.osd.screen.blit(self.surface, self.get_position())
        
 
    def _erase(self):
        # XXX Currently erasing is handled by the parent object.
        self.osd.screen.blit(self.bg_image, self.get_position(), self.get_rect())
        
        
