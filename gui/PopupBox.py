#!/usr/bin/env python
#-----------------------------------------------------------------------
# PopupBox - A dialog box for freevo.
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
A Dialog box type class for Freevo.
""" 
__date__    = "$Date$"
__version__ = "$Revision$" 
__author__  = """Thomas Malt <thomas@malt.no>"""

import osd_sdl
import config

from GUIObject import *
from Color     import *
from Border    import *
from Label     import *

osd = osd_sdl.get_singleton()

class PopupBox(GUIObject):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    icon      icon
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    
    Trying to make a standard popup/dialog box for various usages.
    """
    
    def __init__(self, left=None, top=None, width=None, height=None,
                 text=None, bg_color=None, fg_color=None, icon=None,
                 border=None, bd_color=None, bd_width=None):
        """
        Create a PopupBox object.
        """
        self.text     = None
        self.icon     = None
        self.border   = None
        self.label    = None
        self.bd_color = Color(osd.default_fg_color) # Border color

        GUIObject.__init__(self, left, top, width, height, bg_color, fg_color)
        
        # If some of these are still not set we set them to "our default.
        if not self.left:     self.left   = osd.width/2 - 180
        if not self.top:      self.top    = osd.height/2 - 10
        if not self.width:    self.width  = 360
        if not self.height:   self.height = 60
        if not self.bg_color: Color(osd.default_bg_color)
        if not self.fg_color: Color(osd.default_fg_color)
        
        if text:     self.text   = text
        if icon:     self.icon   = icon

        if bd_color:
            # XXX Do I really need to handle bd_color here? Can't I just
            # XXX pass it to border?
            if isinstance(bd_color, Color):
                self.bd_color = bd_color
            else:
                self.bd_color.set_color(bd_color)

        if border:
            if isinstance(border, Border):
                self.border = border # Do sanity checking inside border
            else:
                self.border = Border(self, border, bd_color, bd_width)

        if type(text) is StringType:
            self.label = Label( text )
            # These values can also be maipulated by the user through
            # get_font and set_font functions.
            self.label.set_font( config.OSD_DEFAULT_FONTNAME,
                                 config.OSD_DEFAULT_FONTSIZE )

            # XXX Set the background color to none so it is transparent.
            self.label.set_background_color( None )
            
        if DEBUG: print "Text: ", text
        if DEBUG: print "Icon: ", icon
        
        
                
    def get_text(self):
        """
        Get the text to display

        Arguments: None
          Returns: text
        """
        return self.text

    def set_text(self, text):
        """
        text  Text to display.
        
        Set text to display

        Arguments: text
          Returns: None
        """
        # XXX Hm.. I should try to do more intelligent parsing and quessing
        # XXX here.
        self.text = text
        if not self.label:
            self.label = Label(text)
        else:
            self.label.set_text(text)

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

        
    def _draw(self):
        """
        The actual internal draw function.

        Arguments: None
          Returns: None
           Throws: TypeError
        """
        if not self.width or not self.height or not self.text:
            raise TypeError, 'Not all needed variables set.'

        c   = self.bg_color.get_color_sdl()
        box = pygame.Surface(self.get_size(), 0, 32)
        box.fill(c)

        s = self.label.surface
        if not s:
            s = self.label._draw()
        if not s:
            raise TypeError, 'No label surface'
        
        box.blit( s,(10,10) )
        x,y = self.get_position()

        osd.screen.blit(box, self.get_position())
        if self.border: self.border._draw()
    

    def _erase(self):
        """
        Erasing us from the canvas without deleting the object.
        """

        if DEBUG: print "  Inside PopupBox._erase..."
        # Only update the part of screen we're at.
        osd.screen.blit(self.bg_image, self.get_position(),
                        self.get_rect())
        
        if self.border:
            if DEBUG: print "    Has border, doing border erase."
            self.border._erase()

        if DEBUG: osd.update()
        if DEBUG: print "    ...", self
        if DEBUG: wait_loop()

