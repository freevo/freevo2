# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Border - For drawing borders around rectangular objects.
# -----------------------------------------------------------------------
# $Id$
#
# Todo: o Make a get_thickness set_thickness function pair.
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.11  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.10  2004/02/18 21:52:04  dischi
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
For drawing borders around rectangular objects.

Border can only be used when called from other GUI Objects. If no
parent object is passed on creation Border will raise an exception.

All suggestions on improvement are welcome
"""

__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


import config
from GUIObject import *

class Border(GUIObject):
    """
    Draw borders around objects. 

    Border can only be used when called from other GUI Objects. If no
    parent object is passed on creation Border will raise an exception.

    All suggestions on improvement are welcome.
    """

    # Define the different borders:
    BORDER_FLAT   = 'flat'
    BORDER_SHADOW = 'shadow'
    BORDER_RAISED = 'raised'
    BORDER_SUNKEN = 'sunken'

    def __init__(self, parent, style=None, color=None, width=None):
        """
        parent  the object to draw border of. use this to get
                geometry and stuff.
        style   Border Type. One of 'flat','shadow','raised' or
                'sunken'
        color   Color of object, Either a Freevo Color object
                or a color integer.
        width   Thickness of border.
        """
        if not parent or not isinstance(parent, GUIObject):
            raise TypeError, 'You need to set the parent correctly'

        self.bd_types = [self.BORDER_FLAT, self.BORDER_SHADOW,
                         self.BORDER_RAISED, self.BORDER_SUNKEN]

        if width and type(width) is IntType:
            self.thickness = width
        else:
            self.thickness = 1
            
        self.style     = self.BORDER_FLAT
        self.rect      = None
        self.shadow_ho = 6          # Horisontal offset for dropshadow
        self.shadow_vo = 6          # Vertical offset for dropshadow

        if style and style in self.bd_types: self.style = style

        GUIObject.__init__(self, 0, 0, parent.width,
                           parent.height)

        parent.add_child(self)

        self.color     = Color(self.osd.default_fg_color)

    def get_style(self):
        """
        Return the style of the border.
        """
        return self.style


    def set_style(self, style):
        """
        Set the which style to draw the border.
        """
        if style in self.bd_types: self.style = style
        else: raise TypeError, style

        
    def _draw(self):
        """
        Draws the border around the parent.

        Todo: Implement what to do for other borders than flat.
        """
        _debug_("  Inside Border.draw...", 2)
        _debug_("  Border type: %s" % self.style, 2)

        # XXX Hack to make border draw inside the areas we expect.
        if self.style == self.BORDER_FLAT:
            c = self.color.get_color_sdl()
            w, h = self.parent.surface.get_size()
            self.rect = self.osd.drawbox(0, 0, w, h, self.thickness, 0, 0x00000000,
                                         self.parent.surface)

        # if self.style == self.BORDER_SHADOW:
        #    self.rect = pygame.draw.rect(self.osd.screen, color, rect,
        #                               self.thickness)
        #    
        #if self.style == self.BORDER_RAISED:
        #    self.rect = pygame.draw.rect(self.osd.screen, color, rect,
        #                               self.thickness)
        #
        #if self.style == self.BORDER_SUNKEN:
        #    self.rect = pygame.draw.rect(self.osd.screen, color, rect,
        #                               self.thickness)
        #


