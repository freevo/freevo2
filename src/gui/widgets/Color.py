# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# color - A color handling object
# -----------------------------------------------------------------------
# $Id$
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.5  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.4  2004/02/18 21:52:04  dischi
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
# -----------------------------------------------------------------------
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
A color handling object.
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""

import osd

from types      import *
from exceptions import *


class Color:
    """
    General Color utility class for Freevo.
    
    I like SDL's way of handling color, but we want to be able to do
    both Freevo old way and SDL, 'so why not make a class?' I said to
    myself.

    All Freevo GUI objects take Color objects as color input. Can also do
    translation between different color formats.
    """
    def __init__(self, in_color=None):
        self.red   = 0
        self.green = 0
        self.blue  = 0
        self.alpha = 0

        self.osd = osd.get_singleton()

        if in_color: self.set_color(in_color)


    def get_color_sdl(self):
        """
        Returns color of Color as SDL list.
        """
        return (self.red, self.green, self.blue, self.alpha)

    def get_color_trgb(self):
        """
        Returns color of Color as TRGB integer
        """
        return self.sdl_to_trgb(self.get_color_sdl())

    def get_color_rgb(self):
        """
        Return nothing but the RGB values ignoring alpha
        """
        return (self.red, self.green, self.blue)

    def set_color(self, color):
        """
        Set color of Color

        Arguments: color, either TRGB integer or SDL list.
        """
        if type(color) == IntType or type(color) == LongType:
            self.red, self.green, self.blue, self.alpha = self.trgb_to_sdl(color)
        elif(type(color) == ListType or
             type(color) == TupleType):
            self.red   = color[0]
            self.green = color[1]
            self.blue  = color[2]
            self.alpha = color[3]
            
        else:
            raise BadColorException, type(color)

    def get_red(self):
        """
        Get level of red in Color
        """
        return self.red
    
    def get_green(self):
        """
        Get level of green in Color
        """
        return self.green
    
    def get_blue(self):
        """
        Get level of blue in Color
        """
        return self.blue
    
    def get_alpha(self):
        """
        Get level of alpha in Color
        """
        return self.alpha
    
    def set_red(self, val):
        """
        Set level of red in Color
        """
        if type(val) == IntType and val >= 0 and val < 256:
            self.red = val
        else:
            raise BadColorException, val
        
    def set_green(self, val):
        """
        Set level of green in Color
        """
        if type(val) == IntType and val >= 0 and val < 256:
            self.green = val
        else:
            raise BadColorException, val

    def set_blue(self, val):
        """
        Set level of blue in Color
        """
        if type(val) == IntType and val >= 0 and val < 256:
            self.blue = val
        else:
            raise BadColorException, val

    def set_alpha(self, val):
        """
        Set transparency level of Color.

        0 is fully transparent, 255 is fully opaque.

        Arguments: Integer 0-255
        """
        if type(val) == IntType and val >= 0 and val < 256:
            self.alpha = val
        else:
            raise BadColorException, val
    
    def trgb_to_sdl(self, color):
        """
        Translates TRGB color integer to SDL color list (R,G,B,A)

        Arguments: TRGB 32bit color integer.
        Returns:   SDL color list (R,G,B,A)
        """
        if not type(color) == IntType and not type(color) == LongType:
            raise BadColorException, type(color)
        
        return self.osd._sdlcol(color)

    def sdl_to_trgb(self, color):
        """
        Translates SDL color list to TRGB color integer.

        Arguments: SDL color list
        Returns:   TRGB color integer.
        """
        if(not type(color) == ListType and
           not type(color) == TupleType):
            raise BadColorException, type(color)
        
        return (((255-color[3]) << 24) + (color[0] << 16) +
                (color[1] << 8) + (color[2] << 0))


