# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Label - A class for text labels
# -----------------------------------------------------------------------
# $Id$
#
# Todo: o Do check to see if font has changed on draw to let people
#         change font between updates.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.26  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.25  2004/02/24 18:56:09  dischi
# add hfill to text_prop
#
# Revision 1.24  2004/02/18 21:52:04  dischi
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


from GUIObject import *

class Label(GUIObject):
    """
    text    String, text to display
    align   Integer, h_align of text. Label.CENTER, Label.RIGHT,
            Label, LEFT
    parent  GUIObject, Reference to object containing this label.
    text_prop A dict of 4 elements composing text proprieties:
              { 'align_h' : align_h, 'align_v' : align_v, 'mode' : mode, 'hfill': hfill }
                 align_v = text vertical alignment
                 align_h = text horizontal alignment
                 mode    = hard (break at chars); soft (break at words)
                 hfill   = True (don't shorten width) or False
    
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

        self.text               = None
        self.font               = None
        self.font_name          = None
        self.font_size          = None
        self.v_margin           = 0
        self.h_margin           = 0

        if parent:
            (state, filename, size, color) = parent.get_font()
            self.set_font(filename, size, color)
            self.set_h_margin(parent.h_margin)
            self.set_v_margin(parent.v_margin)
            parent.add_child(self)
            if not text_prop and hasattr(parent, 'text_prop'):
                text_prop = parent.text_prop

        self.text_prop = text_prop or { 'align_h': 'left',
                                        'align_v': 'top',
                                        'mode'   : 'hard',
                                        'hfill'  : False }
        if text:
            self.set_text(text)


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
            self.text = text
        else:
            raise TypeError, type(text)

        self.width  = -1
        self.height = -1


    def set_font(self, font=None, size=None, color=None):
        """
        font  String. Filename of font to use.
        size  Size in pixels to render font.
        
        Sets the font of label.
        Uses _getfont in osd, and the fontcache in osd.
        """
        if type(font) in StringTypes and type(size) is IntType:
            self.font = self.osd.getfont(font, size)
        else:
            raise TypeError, 'font'

        if isinstance(color, Color):
            self.fg_color = color
        else:
            self.fg_color = self.parent.fg_color
            
        self.font_name = font
        self.font_size = size
        self.width     = -1
        self.height    = -1

            
    def get_font(self):
        """
        Returns the fontobject.
        """
        return self.font


    def get_rendered_size(self):
        align_h = self.text_prop.setdefault( 'align_h', 'left' )
        align_v = self.text_prop.setdefault( 'align_v', 'top' )
        mode    = self.text_prop.setdefault( 'mode', 'hard' )
        hfill   = self.text_prop.setdefault( 'hfill', False )
        data = self.osd.drawstringframed(self.text, 0, 0, self.width, self.height,
                                         self.osd.getfont(self.font_name, self.font_size),
                                         fgcolor=None, bgcolor=None, align_h=align_h,
                                         align_v=align_v, mode=mode, layer='')[1]

        (ret_x0,ret_y0, ret_x1, ret_y1) = data
        if not hfill:
            self.width  = ret_x1 - ret_x0
        self.height = ret_y1 - ret_y0

        return self.width, self.height



    def _draw(self):
        if not self.font:
            raise TypeError, 'Oops, no font.'
        if not self.text:
            raise TypeError, 'Oops, no text.'

        if self.width < 0:
            return

        fgc  = self.fg_color.get_color_trgb()
        font = self.font_name
        size = self.font_size

        (pw, ph) = self.parent.get_size()

        if self.width > pw:
            self.width = pw
        if self.height > ph:
            self.height = ph

        align_h = self.text_prop[ 'align_h' ]
        align_v = self.text_prop[ 'align_v' ]
        mode    = self.text_prop[ 'mode' ]

        self.surface = self.get_surface()
        r = self.osd.drawstringframed(self.text, 0, 0, self.width, self.height,
                                      self.osd.getfont(font, size), fgcolor=fgc,
                                      bgcolor=None, align_h=align_h,
                                      align_v=align_v, mode=mode,
                                      layer=self.surface)[1]

        return_x0,return_y0, return_x1, return_y1 = r
        if not self.text_prop.setdefault( 'hfill', False ):
            self.width  = return_x1 - return_x0
        self.height = return_y1 - return_y0
