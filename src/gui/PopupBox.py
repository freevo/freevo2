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
# Revision 1.32  2003/09/13 10:32:56  dischi
# fix a font problem and cleanup some unneeded stuff
#
# Revision 1.31  2003/09/11 19:34:18  outlyer
# Revert this change; I forgot that get_size returns a tuple.
#
# Revision 1.30  2003/09/11 14:13:55  outlyer
# Another warning fix.
#
# Revision 1.29  2003/09/07 11:17:21  dischi
# add basic refresh function
#
# Revision 1.28  2003/09/06 17:12:50  rshortt
# For Label use parent's text_prop if available before resorting to defaults.
#
# Revision 1.27  2003/09/06 13:29:00  gsbarbieri
# PopupBox and derivates now support you to choose mode (soft/hard) and
# alignment (vertical/horizontal).
#
# Revision 1.26  2003/09/05 15:59:20  outlyer
# Use StringTypes instead of "StringType" since StringTypes includes unicode,
# which TV listings are sometimes in (like mine)
#
# The change to the StringTypes tuple has existed since Python 2.2 (at least)
# so it should be fine.
#
# This prevents massive explosions on mine.
#
# Revision 1.25  2003/09/03 21:02:44  outlyer
# Left in a debug line
#
# Revision 1.24  2003/09/01 18:50:56  dischi
# Set default width and height based on screen size and size of the text
# in it. This avoids ugly line breaks
#
# Revision 1.23  2003/07/20 09:46:11  dischi
# Some default width fixes to match the current new default font. It would
# be great if a box without width and height could be as big as needed
# automaticly (with a max width). Right now, the buttons in the ConfirmBox
# are not at the bottom of the box, that should be fixed.
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

import rc
import event as em

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
    text_prop A dict of 3 elements composing text proprieties:
              { 'align_h' : align_h, 'align_v' : align_v, 'mode' : mode }
                 align_v = text vertical alignment
                 align_h = text horizontal alignment
                 mode    = hard (break at chars); soft (break at words)
    
    Trying to make a standard popup/dialog box for various usages.
    """
    
    def __init__(self, parent='osd', text=' ', handler=None, left=None, 
                 top=None, width=0, height=0, bg_color=None, fg_color=None,
                 icon=None, border=None, bd_color=None, bd_width=None,
                 vertical_expansion=1, text_prop=None):

        self.handler = handler
        Container.__init__(self, 'frame', left, top, width, height, bg_color, 
                           fg_color, None, None, border, bd_color, bd_width,
                           vertical_expansion)

        self.text_prop = text_prop or { 'align_h': 'left',
                                   'align_v': 'top',
                                   'mode'   : 'soft' }

        if not parent or parent == 'osd':
            parent = self.osd.app_list[0]

        parent.add_child(self)

        if DEBUG: print 'set focus to %s' % self
        self.osd.add_app(self)

        self.event_context = 'input'
        rc.set_context(self.event_context) 

        self.internal_h_align = Align.CENTER
        self.internal_v_align = Align.CENTER

        # In the future we will support duration where the popup
        # will destroy() after x seconds.
        self.duration = 0

        self.font = None
        if self.skin_info_font:       
            self.set_font(self.skin_info_font.name, 
                          self.skin_info_font.size, 
                          self.fg_color)
        else:
            self.set_font(config.OSD_DEFAULT_FONTNAME,
                          config.OSD_DEFAULT_FONTSIZE)
                
        if not width:
            tw = self.font.font.stringsize(text) + self.h_margin*2
            if tw < self.osd.width * 2 / 3:
                self.width = max(self.osd.width / 2, tw)
            else:
                self.width  = self.osd.width / 2
            
        if not height:
            self.height = self.osd.height / 4

        if not self.left:
            self.left = self.osd.width/2 - self.width/2
        if not self.top:
            self.top  = self.osd.height/2 - self.height/2

        if type(text) in StringTypes:
            self.label = Label(text, self, Align.CENTER, Align.CENTER,
                               text_prop=self.text_prop )
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
        return ('normal', self.font.name, int(self.font.size), self.font.color)


    def set_font(self, file, size, color):
        """
        Set the font.

        Just hands the info down to the label. Might raise an exception.
        """
        if not self.font:
            self.font = self.osd.getfont(file, size)

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
        if type(image) in StringTypes:
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

        self.blit_parent()

    
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


    def refresh(self):
        """
        draw and update the screen
        """
        self.draw()
        self.osd.update()

        
    def eventhandler(self, event):
        if DEBUG: print 'PopupBox: event = %s' % event

        elif event == em.INPUT_EXIT:
            self.destroy()
        else:
            return self.parent.eventhandler(event)

