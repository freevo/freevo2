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
# Revision 1.17  2003/07/07 17:10:46  dischi
# small fix. Someone should clean up all the gui font stuff and use OSDFont for it
#
# Revision 1.16  2003/07/07 16:24:55  dischi
# changes to work with the new drawstringframed
#
# Revision 1.15  2003/07/05 09:10:23  dischi
# revert some changes to work with the new drawstringframed
#
# Revision 1.14  2003/07/02 20:11:43  dischi
# use now the calc part of drawstringframed
#
# Revision 1.13  2003/06/26 01:46:49  rshortt
# Set DEBUG back to 0 as to not annoy everyone with my insane debug statements
# which I still need to help with gui development. :)
#
# Revision 1.12  2003/06/26 01:41:16  rshortt
# Fixed a bug wit drawstringframed hard.  Its return coords were always 0's
# which made it impossible to judge the size.
#
# Revision 1.11  2003/06/25 02:27:39  rshortt
# Allow 'frame' containers to grow verticly to hold all contents.  Also
# better control of object's background images.
#
# Revision 1.10  2003/05/21 00:04:25  rshortt
# General improvements to layout and drawing.
#
# Revision 1.9  2003/05/16 02:11:50  rshortt
# Fixed a nasty label alingment-bouncing bug.  There are lots of leftover
# comments and DEBUG statements but I will continue to make use of them
# for improvements.
#
# Revision 1.8  2003/05/04 23:12:35  rshortt
# Dumb typo.
#
# Revision 1.7  2003/05/04 22:50:12  rshortt
# Fix for some crashes with text wrapping.
#
# Revision 1.6  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.5  2003/04/24 19:56:20  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.4  2003/03/02 20:15:41  rshortt
# GUIObject and PopupBox now get skin settings from the new skin.  I put
# a test for config.NEW_SKIN in GUIObject because this object is used by
# MenuWidget, so I'll remove this case when the new skin is finished.
#
# PopupBox can not be used by the old skin so anywhere it is used should
# be inside a config.NEW_SKIN check.
#
# PopupBox -> GUIObject now has better OOP behaviour and I will be doing the
# same with the other objects as I make them skinnable.
#
# Revision 1.3  2003/02/23 18:21:50  rshortt
# Some code cleanup, better OOP, influenced by creating a subclass of
# RegionScroller called ListBox.
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
    
    def __init__(self, text=None, parent=None, h_align=None, v_align=None, 
                 width=-1, height=-1):

        GUIObject.__init__(self, width=width, height=height)

        if h_align:
            self.h_align  = h_align
        else:
            self.h_align  = Align.LEFT

        if v_align:
            self.v_align  = v_align
        else:
            self.v_align  = Align.CENTER

        self.text     = None
        self.font     = None # This is a OSD.Font object not pygame.
        self.font_name = None
        self.font_size = None
        self.selected_font_name = None
        self.selected_font_size = None
        self.v_margin = 0
        self.h_margin = 0
        self.set_background_color(None)

        if parent:
            (state, filename, size, color) = parent.get_font()
            self.set_font(state, filename, size, color)
            self.set_h_margin(parent.h_margin)
            self.set_v_margin(parent.v_margin)
            parent.add_child(self)
        
        if text:    self.set_text(text)


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

        # self.width = -1
        # self.height = -1
        self.surface_changed = 1


    def set_font(self, state='normal', font=None, size=None, color=None):
        """
        font  String. Filename of font to use.
        size  Size in pixels to render font.
        
        Sets the font of label.
        Uses _getfont in osd, and the fontcache in osd.
        """
        if DEBUG: print 'LABEL: state=%s' % state
        if DEBUG: print 'LABEL: font=%s' % font
        if DEBUG: print 'LABEL: size=%s' % size

        if type(font) is StringType and type(size) is IntType:
            if self.surface: self.surface = None
            self.font = self.osd.getfont(font, size)
        else:
            raise TypeError, 'font'

        if state == 'normal':
            if isinstance(color, Color):
                self.fg_color = color
            else:
                self.fg_color = self.parent.fg_color

            self.font_name = font
            self.font_size = size
        elif state == 'selected':
            if isinstance(color, Color):
                self.selected_fg_color = color
            else:
                self.selected_fg_color = self.parent.selected_fg_color

            self.selected_font_name = font
            self.selected_font_size = size

        self.surface_changed = 1

            
    def get_font(self):
        """
        Returns the fontobject.

        We keep a copy of _this_ font object inside 
        """
        return self.font


    def get_rendered_size(self):
        data = self.osd.drawstringframed(self.text, 0, 0, self.width, self.height,
                                         self.osd.getfont(self.font_name, self.font_size),
                                         fgcolor=None, bgcolor=None, align_h='left',
                                         align_v='top', mode='hard', layer='')[1]


        (ret_x0,ret_y0, ret_x1, ret_y1) = data

        # LABEL: ,71,17,294,43
        self.width = ret_x1 - ret_x0
        # self.width = ret_x1
        # self.width = self.surface.get_width()
        self.height = ret_y1 - ret_y0
        # self.height = self.surface.get_height()
        # self.height = ret_y1

        return self.width, self.height



    def render(self):
        if DEBUG: print 'Label::_draw %s' % self
        if DEBUG: print '       text=%s' % self.text

        if not self.font: raise TypeError, 'Oops, no font.'
        if not self.text: raise TypeError, 'Oops, no text.'

        if self.width < 0:
            self.surface_changed = 1
            return

        if self.parent.selected: 
            if DEBUG: print '       SELECTED'
            fgc = self.selected_fg_color.get_color_trgb()
            font = self.selected_font_name
            size = self.selected_font_size
        else:
            if DEBUG: print '       NOT SELECTED'
            fgc = self.fg_color.get_color_trgb()
            font = self.font_name
            size = self.font_size

        if DEBUG: print '       fgc=%s' % fgc

        (pw, ph) = self.parent.get_size()
        if self.width > pw: self.width = pw
        if self.height > ph: self.height = ph
        self.surface = self.parent.surface.subsurface((self.left, self.top, self.width, self.height))
        if DEBUG: print '       surface=%s' % self.surface

        (rest_words, (return_x0,return_y0, return_x1, return_y1)) = \
                     self.osd.drawstringframed(self.text, 0, 0, self.width, self.height,
                                               self.osd.getfont(font, size), fgcolor=fgc,
                                               bgcolor=None, align_h='left',
                                               align_v='top', mode='hard',
                                               layer=self.surface)

        if DEBUG: print '       %s,%s,%s,%s,%s' % (rest_words,return_x0,return_y0,
                                                   return_x1,return_y1)
        # LABEL: ,71,17,294,43
        self.width = return_x1 - return_x0
        # self.width = return_x1
        # self.width = self.surface.get_width()
        self.height = return_y1 - return_y0
        # self.height = self.surface.get_height()
        # self.height = return_y1 

        if DEBUG: print '       parent="%s"' % self.parent
        if DEBUG: print '       self.surface="%s"' % self.surface
        if DEBUG: print '       surface.rect: %s' % self.surface.get_rect()
        if DEBUG: print '       self.rect: %s,%s,%s,%s' % self.get_rect()
        if DEBUG: print '       parent.surface="%s"' % self.parent.surface
        if DEBUG: print '       position="%s,%s"' % self.get_position()


    def _draw(self):
        self.render()

        if DEBUG: print '       draw position="%s,%s"' % self.get_position()
        self.blit_parent()
        
 
    def _erase(self):
        # XXX Currently erasing is handled by the parent object.
        self.osd.screen.blit(self.bg_image, self.get_position(), self.get_rect())
        
        
