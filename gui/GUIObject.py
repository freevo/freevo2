#!/usr/bin/env python
#-----------------------------------------------------------------------
# GUIObject - Common object for all GUI Classes
#-----------------------------------------------------------------------
# $Id$
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
A Object Oriented GUI Widget library for Freevo

This is aimed at being a general library for GUI programming with Freevo.
It is built directly on top of SDL with pygame, and it's aimed at being
fairly fast.

Event though the library is built from the ground the design is heavy
influenced by other GUI toolkits, such as Java JDK and QT.

Currently not many classes are in place, but hopefully we will add more
in time.
"""
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""


import ZIndexRenderer

from gui.Color import *

DEBUG = 0

zir = ZIndexRenderer.get_singleton()

class GUIObject:
    """
    Common parent class of all GUI objects. You can override this to make
    new Widgets.
    """

    def __init__(self, left=None, top=None, width=None, height=None,
                 bg_color=None, fg_color=None):
        """
        Constructor. Creates the inital object.

        Todo: I should off course check if input values are valid.
        """
        self.left     = 0
        self.top      = 0
        self.width    = 0
        self.height   = 0
        self.visible  = 0
        self.bg_color = Color( osd.default_bg_color )
        self.fg_color = Color( osd.default_fg_color )
        self.bg_image = None
        
        if DEBUG: print "inside GUIOBJECT INIT"

        # XXX At the moment we know about this since I hardcoded it, but
        # XXX maybe it's a good idea to supply zindex object at construction
        # XXX maybe get_zindex_handler and set_zindex_handler function.s
        self.zindex_pos = zir.add_object(self)
        
        if left:   self.left   = left
        if top:    self.top    = top
        if width:  self.width  = width
        if height: self.height = height

        if bg_color:
            if isinstance(bg_color, Color):
                self.bg_color = bg_color
            else:
                self.bg_color.set_color(bg_color)
                
        if fg_color:
            if isinstance(fg_color, Color):
                self.fg_color = fg_color
            else:
                self.fg_color.set_color(fg_color)
                

    def get_rect(self):
        """
        Return SDL rect information for the object.

        Returns: left,top,width,height
        """
        return (self.left, self.top, self.width, self.height)

    def get_position(self):
        """
        Gets the coordinates of PopupBox

        Arguments: None
        Returns:   (x, y) - The coordinates of top left coner as list.
        """
        return (self.left, self.top)

    def set_position(self, left, top):
        """
        Set the position of PopupBox

        Arguments: left - left corner
                   top - top corner
        returns:   None
        """
        self.left = left
        self.top = top


    def get_size(self):
        """
        Get the width and height of box

        Arguments: None
        Returns:   (width, height) - as list.
        """
        return (self.width, self.height)

    def set_size(self, width, height):
        """
        Set the width adn height of box

        Arguments: width, height
          Returns: None
        """
        self.width  = width
        self.height = height

    def get_foreground_color(self):
        """
        Returns the foreground color of object
        """
        return self.fg_color
    
    def set_foreground_color(self, color):
        """
        Sets the foreground color of object.
        """
        if isinstance(color, Color):
            self.fg_color = color
        else:
            raise BadColorException, type(color)
           
    def get_background_color(self):
        """
        Returns the background color of object.
        """
        return self.bg_color
    
    def set_background_color(self, color):
        """
        Sets the background color of object.

        If None background color will be transparent.
        """
        if isinstance(color, Color):
            self.bg_color = color
        elif not color:
            self.bg_color = None
        else:
            raise BadColorException, type(color)

    def show(self):
        """
        Shows the object.

        This is really handled by the render object.
        """
        zir.update_show(self)
        self.visible = 1    

    def hide(self):
        """
        Hide the object.

        A lot of stuff updating the display is done by the reder object.
        """
        if DEBUG: pygame.image.save( self.bg_image, '/tmp/object_hide.bmp' )
        if DEBUG: print "   Inside hide.. check picture"
        if DEBUG: wait_loop()
        self._erase()
        self.visible = 0
        zir.update_hide(self)

    def is_visible(self):
        """
        Returns whether the object is visible or not.

        Returns: 0 or 1 
        """
        return self.visible
    
    def redraw(self):
        """
        Does a redraw of the object.

        At the moment not implemented.
        """
        pass

