#!/usr/bin/env python
#-----------------------------------------------------------------------
# Border - For drawing borders around rectangular objects.
#-----------------------------------------------------------------------
# $Id$
#
# Todo: o Make a get_thickness set_thickness function pair.
#-----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/02/18 13:40:52  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
#
# Revision 1.1  2002/12/07 15:21:31  dischi
# moved subdir gui into src
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
For drawing borders around rectangular objects.

Border can only be used when called from other GUI Objects. If no
parent object is passed on creation Border will raise an exception.

All suggestions on improvement are welcome
"""

__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


import pygame

from GUIObject import *

DEBUG = 0


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
            
        self.parent    = parent
        self.style     = self.BORDER_FLAT
        self.rect      = None
        self.shadow_ho = 6          # Horisontal offset for dropshadow
        self.shadow_vo = 6          # Vertical offset for dropshadow

        if style and style in self.bd_types: self.style = style

        GUIObject.__init__(self, parent.left, parent.top, parent.width,
                           parent.height)

        self.color     = Color(self.osd.default_fg_color)

    def get_erase_rect(self):
        """
        Returns the rectangle to erase on updates.

        The borders are drawn both on the outside and the inside of the
        rect that defines it. Therefore We don't get complete accuracy
        when updating boxes with borders. This function is part of
        working around that.

        Suggestions on how to improve this are welcome.

        Returns: (left,top,width,height) - a pygame rect.
        """
        x = self.left-(round(self.thickness/2)-1)
        y = self.top-(round(self.thickness/2)-1)
        w = self.width+self.thickness*2
        h = self.height+self.thickness*2
        return (x,y,w,h)

 
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
        if DEBUG: print "  Inside Border._draw..."
        if DEBUG: print "  Border type: ", self.style

        # XXX Hack to make border draw inside the areas we expect.
        if self.style == self.BORDER_FLAT:
            c = self.color.get_color_sdl()
            self.rect = pygame.draw.rect(self.osd.screen, c, self.get_rect(),
                                         self.thickness)

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


    def _erase(self):
        """
        Erases the border from screen.
        """
        # XXX Hm.. pygame.draw.rect draws border outside bounding box.
        # XXX Making hack to fix, but should be done proper.

        if DEBUG: print "    Inside Border erase."
        x,y,w,h = self.get_erase_rect()
        
        if DEBUG: print " Thick: ", self.thickness
        if DEBUG: print " Width: ", w
        self.osd.screen.blit(self.parent.bg_image, (x,y), (x,y,w,h))
        if DEBUG: save_image(self)
        if DEBUG: print "    Waiting at bottom of border erase"
        if DEBUG: self.osd.update()
        if DEBUG: wait_loop()

