#!/usr/bin/env python
#-----------------------------------------------------------------------
# .py - 
#-----------------------------------------------------------------------
# $Id$
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/02/18 21:52:04  dischi
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
# Revision 1.2  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.1  2003/07/14 19:39:01  rshortt
# A new class for having a small video preview window.  It doesn't work yet!
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

import config
from gui.GUIObject      import *
from gui.Color import Color
from gui.Border import Border

class VideoBox(GUIObject):
    """
    """

    def __init__(self, parent=None, left=100, top=100, width=100, height=100, 
                 border=None, bd_color=None, bd_width=None):

        GUIObject.__init__(self, left, top, width, height)

        if not parent:
            parent = self.osd.focused_app
        self.parent = parent

        self.border         = border
        self.bd_color       = bd_color
        self.bd_width       = bd_width


        if not self.bd_color:
            if self.skin_info_widget.rectangle.color:
                self.bd_color = Color(self.skin_info_widget.rectangle.color)
            else:
                self.bd_color = Color(self.osd.default_fg_color)
    
        if not self.bd_width:
            if self.skin_info_widget.rectangle.size:
                self.bd_width = self.skin_info_widget.rectangle.size
            else:
                self.bd_width = 2
    
        if not self.border:
            self.border = Border(self, Border.BORDER_FLAT,
                                 self.bd_color, self.bd_width)


    def _draw(self):
        _debug_('VideoBox::_draw %s' % self, 2)
            
        if not self.width or not self.height:
            raise TypeError, 'Not all needed variables set.'
        
        self.surface = self.osd.Surface(self.get_size(), 0, 32)

        c   = self.bg_color.get_color_sdl()
        a   = self.bg_color.get_alpha()
        self.surface.fill(c)
        self.surface.set_alpha(a)

        self.blit_parent()
        self.play_movie()


    def play_movie(self):
        import pygame
        movie = pygame.movie.Movie('/var/tmp/test.mpeg')
        movie.set_display(self.osd.screen)
        movie.play()
