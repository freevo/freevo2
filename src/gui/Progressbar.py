# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Progressbar.py - a simple progress bar
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/07/10 12:33:39  dischi
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
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al.
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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
# ----------------------------------------------------------------------- */


import config

from GUIObject import *
from Container import Container


class Progressbar(Container):
    """
    x         x coordinate. Integer
    y         y coordinate. Integer
    width     Integer
    height    Integer
    bg_color  Background color (Color)
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    def __init__(self, x=None, y=None, width=70, height=25, bg_color=None,
                 border=None, bd_color=None, bd_width=None, full=0):
        
        Container.__init__(self, 'widget', x, y, width, height, bg_color,
                           0, 0, 0, border, bd_color, bd_width)

        self.h_margin = 2
        self.v_margin = 2
        self.position = 0
        self.full     = full

        self.set_v_align(Align.BOTTOM)
        self.set_h_align(Align.CENTER)



    def _draw(self):
        if not self.width or not self.height:
            raise TypeError, 'Not all needed variables set.'

        position = (self.position * 100) / self.full 
        width, height = self.get_size()

        self.surface = self.get_surface()

        self.surface.fill(self.bg_color.get_color_sdl())
        self.surface.set_alpha(self.bg_color.get_alpha())

        box = self.osd.Surface(((width * position ) / 100 , height), 0, 32)
        box.fill(self.selected_bg_color.get_color_sdl())
        box.set_alpha(self.selected_bg_color.get_alpha())

        self.surface.blit(box, (0,0))
        Container._draw(self)


    def tick(self):
        if self.position < self.full:
            self.position += 1
