#!/usr/bin/env python
#-----------------------------------------------------------------------
# PopupBox - A dialog box for freevo.
#-----------------------------------------------------------------------
# $Id$
#
# Todo: o Add sanitychecking on all arguments.
#       o Add actual support for icons, not just brag about it.
#       o Start using the OSD imagecache for rectangles.
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.19  2003/05/21 00:02:02  rshortt
# Labels are now handled better and there is no need for the Panel class here.
#
# Revision 1.18  2003/05/04 23:18:19  rshortt
# Change some height values (temporarily) to avoid some crashes.
#
# Revision 1.17  2003/05/04 22:50:12  rshortt
# Fix for some crashes with text wrapping.
#
# Revision 1.16  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.15  2003/04/24 19:56:27  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.14  2003/04/20 13:02:29  dischi
# make the rc changes here, too
#
# Revision 1.13  2003/04/06 21:08:52  dischi
# Make osd.focusapp the default parent (string "osd").
# Maybe someone should clean up the paramter, a PopupBox and an Alertbox
# needs no colors because they come from the skin and parent should be
# the last parameter.
#
# Revision 1.12  2003/03/30 20:50:00  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.11  2003/03/30 18:02:31  dischi
# set parent before calling the parent constructor
#
# Revision 1.10  2003/03/30 17:42:20  rshortt
# Now passing self along to skin.GetPopupBoxStyle in an attempt to get the
# skin propertied of the current menu in case we are using a menu based skin.
#
# Revision 1.2  2002/08/18 21:57:00  tfmalt
# o Added margin handling.
# o Added support for Icons in popupboxes.
# o Addes support for vertical and horizontal alignment.
# o Added a ton more errorhandling.
# o Let Labels draw themselves independently.
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
A Dialog box type class for Freevo.
""" 

import config

from GUIObject import *
from Container import *
from Panel     import *
from Color     import *
from Border    import *
from Label     import *
from types     import *

DEBUG = 0


class PopupBox(Container):
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
    
    def __init__(self, parent='osd', text=' ', handler=None, left=None, 
                 top=None, width=360, height=120, bg_color=None, fg_color=None,
                 icon=None, border=None, bd_color=None, bd_width=None):

        self.handler = handler

        Container.__init__(self, 'frame', left, top, width, height, bg_color, 
                           fg_color, None, None, border, bd_color, bd_width)

        if not parent or parent == 'osd':
            parent = self.osd.focused_app
        parent.add_child(self)

        if DEBUG: print 'set focus to %s' % self
        self.osd.focused_app = self


        self.internal_h_align = Align.CENTER

        # In the future we will support duration where the popup
        # will destroy() after x seconds.
        self.duration = 0

        if not self.left:     self.left   = self.osd.width/2 - self.width/2
        if not self.top:      self.top    = self.osd.height/2 - self.height/2


        self.font = None
        if self.skin_info_font:       
            self.set_font(self.skin_info_font.name, 
                          self.skin_info_font.size, 
                          self.fg_color)
        else:
            self.set_font(config.OSD_DEFAULT_FONTNAME,
                          config.OSD_DEFAULT_FONTSIZE)
                
        if type(text) is StringType:
            self.label = Label(text, self, Align.CENTER, Align.CENTER)
        else:
            raise TypeError, text

        if icon:
            self.set_icon(icon)
                

    def get_text(self):
        """
        Get the text to display

        Arguments: None
          Returns: text
        """
        return self.label.text


    def get_font(self):
        """
        Does not return OSD.Font object, but the filename and size as list.
        """
        return ('normal', self.font.filename, int(self.font.size), self.font.color)


    def set_font(self, file, size, color):
        """
        Set the font.

        Just hands the info down to the label. Might raise an exception.
        """
        if not self.font:
            self.font = Font()

        self.font.filename = file
        self.font.size = size
        self.font.color = color

        # if self.label:
        #     self.label.set_font('normal', file, size, color)
        # else:
        #     raise TypeError, file


    def get_icon(self):
        """
        Returns the icon of the popupbox (if set).
        """
        return self.icon


    def set_icon(self, image):
        """
        Set the icon of the popupbox.
        Also scales the icon to fit the size of the box.
        
        Can either be a string with filename or a pygame Surface object.
        """
        if type(image) is StringType:
            self.icon = pygame.image.load(image).convert_alpha()
        else:
            self.icon = image

        bx,by = self.get_size()
        ix,iy = self.icon.get_size()
        
        aspect = (ix/iy)

        if(bx > by):
            iy = by-(self.v_margin*2)
            ix = iy*aspect
        else:
            ix = bx-(self.h_margin*2)
            iy = ix/aspect
        
        self.icon = pygame.transform.scale(self.icon, (ix, iy))


    def _draw(self):
        """
        The actual internal draw function.

        """
        if DEBUG: print 'PopupBox::_draw %s' % self

        if not self.width or not self.height:
            raise TypeError, 'Not all needed variables set.'

        self.surface = pygame.Surface(self.get_size(), 0, 32)

        c   = self.bg_color.get_color_sdl()
        a   = self.bg_color.get_alpha()
        self.surface.fill(c)
        self.surface.set_alpha(a)
        
        if self.icon:
            # ix,iy = self.get_position()
            self.surface.blit(self.icon, (self.h_margin, self.v_margin)) 

        Container._draw(self)

        # self.parent.surface.blit(self.surface, self.get_position())
        self.osd.screen.blit(self.surface, self.get_position())

    
    def _erase(self):
        """
        Erasing us from the canvas without deleting the object.
        """

        if DEBUG: print "  Inside PopupBox._erase..."
        # Only update the part of screen we're at.
        self.osd.screen.blit(self.bg_surface, self.get_position(),
                        self.get_rect())
        
        if self.border:
            if DEBUG: print "    Has border, doing border erase."
            self.border._erase()

        if DEBUG: print "    ...", self


    def eventhandler(self, event):
        if DEBUG: print 'PopupBox: event = %s' % event

        trapped = [rc.UP, rc.DOWN, rc.LEFT, rc.RIGHT,
                   rc.ENTER, rc.SELECT]

        if trapped.count(event) > 0:
            return
        elif [rc.EXIT, ].count(event) > 0:
            self.destroy()
        else:
            return self.parent.eventhandler(event)

