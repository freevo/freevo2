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
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


import pygame

from GUIObject import *

class Label(GUIObject):
    """
    text   String, text to display
    align  Integer, alignment of text. Label.CENTER, Label.RIGHT, Label, LEFT

    Displays a single line of text. Really it maintains a surface with a
    rendered text. If text is updated text is rerendered and reblitted to
    the screen.

    Both text and align can be set using functions. If text is not set when
    draw is called an exception is raised.
    """
    
    CENTER = 1001
    LEFT   = 1002
    RIGHT  = 1003
    
    def __init__(self, text=None, align=None):
        self.alignment = self.LEFT
        self.text      = None
        self.font      = None # This is a OSD.Font object not pygame.
        self.surface   = None

        GUIObject.__init__(self)

        if align: self.set_alignment(align)
        if text:  self.set_text(text)
        self.set_foreground_color(Color( (0,0,0,255) ))
        
    def get_alignment(self):
        """
        Returns alignment of text.
        """
        return self.alignment

    def get_text(self):
        """
        Returns text.
        """
        return self.text

    def set_alignment(self, align):
        """
        Sets alignment of text.
        """
        if type(align) is IntType and align > 1000 and align < 1004:
                self.alignment = align
        else:
            raise TypeError, align

    def set_text(self, text):
        """
        Sets text.
        """
        if type(text) is StringType:
            self.text = text
        else:
            raise TypeError, text

    def set_font(self, font=None, size=None):
        """
        font  String. Filename of font to use.
        size  Size in pixels to render font.
        
        Sets the font of label.
        Uses _getfont in osd, and the fontcache in osd.
        """
        if type(font) is StringType and type(size) is IntType:
            self.font = self._get_osd_font(font, size)
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
        for f in osd.fontcache:
            if f.filename == filename and f.ptsize == size:
                return f

        font       = pygame.font.Font(filename, size)
        f          = osd_sdl.Font()
        f.filename = filename
        f.ptsize   = size
        f.font     = font

        osd.fontcache.append(f)
        return f
    
    def _draw(self):
        """
        Our default _draw function.
        """
        f   = self.font
        t   = self.text
        fgc = self.fg_color.get_color_sdl()
            
        if not f:
            # XXX Make more extensive tests and exceptions later.
            raise TypeError, f
        if not t:
            # XXX Make more extensive tests and exceptions later.
            raise TypeError, t

        # XXX Currently we don't use background color since that 
        self.surface = f.font.render(t, 1, fgc)
        return self.surface

    def _erase(self):
        pass
        
