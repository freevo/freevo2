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
# Revision 1.23  2004/01/09 02:08:07  rshortt
# GUI fixes from Matthieu Weber.
#
# Revision 1.22  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.21  2003/09/13 10:32:55  dischi
# fix a font problem and cleanup some unneeded stuff
#
# Revision 1.20  2003/09/06 17:12:50  rshortt
# For Label use parent's text_prop if available before resorting to defaults.
#
# Revision 1.19  2003/09/06 13:29:00  gsbarbieri
# PopupBox and derivates now support you to choose mode (soft/hard) and
# alignment (vertical/horizontal).
#
# Revision 1.18  2003/09/05 15:59:20  outlyer
# Use StringTypes instead of "StringType" since StringTypes includes unicode,
# which TV listings are sometimes in (like mine)
#
# The change to the StringTypes tuple has existed since Python 2.2 (at least)
# so it should be fine.
#
# This prevents massive explosions on mine.
#
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

class Label(GUIObject):
    """
    text    String, text to display
    align   Integer, h_align of text. Label.CENTER, Label.RIGHT,
            Label, LEFT
    parent  GUIObject, Reference to object containing this label.
    text_prop A dict of 3 elements composing text proprieties:
              { 'align_h' : align_h, 'align_v' : align_v, 'mode' : mode }
                 align_v = text vertical alignment
                 align_h = text horizontal alignment
                 mode    = hard (break at chars); soft (break at words)
    
    Displays a single line of text. Really it maintains a surface with a
    rendered text. If text is updated text is rerendered and reblitted to
    the screen.

    Both text and align can be set using functions. If text is not set when
    draw is called an exception is raised.
    """
    
    def __init__(self, text=None, parent=None, h_align=None, v_align=None, 
                 width=-1, height=-1, text_prop=None):

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
            if not text_prop and hasattr(parent, 'text_prop'):
                text_prop = parent.text_prop

        self.text_prop = text_prop or { 'align_h': 'left',
                                        'align_v': 'top',
                                        'mode'   : 'hard' }

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
        if type(text) in StringTypes:
            if self.surface: self.surface = None
            self.text = text
        else:
            raise TypeError, type(text)

        self.width = -1
        self.height = -1
        self.surface_changed = 1


    def set_font(self, state='normal', font=None, size=None, color=None):
        """
        font  String. Filename of font to use.
        size  Size in pixels to render font.
        
        Sets the font of label.
        Uses _getfont in osd, and the fontcache in osd.
        """
        _debug_('LABEL: state=%s' % state, 2)
        _debug_('LABEL: font=%s' % font, 2)
        _debug_('LABEL: size=%s' % size, 2)

        if type(font) in StringTypes and type(size) is IntType:
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
        align_h = self.text_prop.setdefault( 'align_h', 'left' )
        align_v = self.text_prop.setdefault( 'align_v', 'top' )
        mode    = self.text_prop.setdefault( 'mode', 'hard' )
        data = self.osd.drawstringframed(self.text, 0, 0, self.width, self.height,
                                         self.osd.getfont(self.font_name, self.font_size),
                                         fgcolor=None, bgcolor=None, align_h=align_h,
                                         align_v=align_v, mode=mode, layer='')[1]


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
        _debug_('Label::_draw %s' % self, 2)
        _debug_('       text=%s' % self.text, 2)

        if not self.font: raise TypeError, 'Oops, no font.'
        if not self.text: raise TypeError, 'Oops, no text.'

        if self.width < 0:
            self.surface_changed = 1
            return

        if self.parent.selected: 
            fgc = self.selected_fg_color.get_color_trgb()
            font = self.selected_font_name
            size = self.selected_font_size
        else:
            fgc = self.fg_color.get_color_trgb()
            font = self.font_name
            size = self.font_size

        (pw, ph) = self.parent.get_size()
        if self.width > pw: self.width = pw
        if self.height > ph: self.height = ph
        self.surface = self.parent.surface.subsurface((self.left, self.top, self.width, self.height))
        align_h = self.text_prop[ 'align_h' ]
        align_v = self.text_prop[ 'align_v' ]
        mode    = self.text_prop[ 'mode' ]

        (rest_words, (return_x0,return_y0, return_x1, return_y1)) = \
                     self.osd.drawstringframed(self.text, 0, 0, self.width, self.height,
                                               self.osd.getfont(font, size), fgcolor=fgc,
                                               bgcolor=None, align_h=align_h,
                                               align_v=align_v, mode=mode,
                                               layer=self.surface)

        # LABEL: ,71,17,294,43
        self.width = return_x1 - return_x0
        # self.width = return_x1
        # self.width = self.surface.get_width()
        self.height = return_y1 - return_y0
        # self.height = self.surface.get_height()
        # self.height = return_y1 

        _debug_('       parent="%s"' % self.parent, 2)
        _debug_('       self.surface="%s"' % self.surface, 2)
        _debug_('       surface.rect: %s' % self.surface.get_rect(), 2)
        _debug_('       self.rect: %s,%s,%s,%s' % self.get_rect(), 2)
        _debug_('       parent.surface="%s"' % self.parent.surface, 2)
        _debug_('       position="%s,%s"' % self.get_position(), 2)


    def _draw(self):
        self.render()

        _debug_('       draw position="%s,%s"' % self.get_position(), 2)
        self.blit_parent()
        
 
    def _erase(self):
        # XXX Currently erasing is handled by the parent object.
        self.osd.screen.blit(self.bg_image, self.get_position(), self.get_rect())
        
        
