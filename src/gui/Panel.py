#!/usr/bin/env python
#-----------------------------------------------------------------------
# Panel.py - A simple subclass of Container
#-----------------------------------------------------------------------
# $Id$
#
#-----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.4  2003/06/25 02:27:39  rshortt
# Allow 'frame' containers to grow verticly to hold all contents.  Also
# better control of object's background images.
#
# Revision 1.3  2003/04/24 19:56:26  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.2  2003/04/22 23:51:22  rshortt
# updates
#
# Revision 1.1  2003/04/09 01:38:10  rshortt
# Initial commit of some in-progress classes.
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

import copy
import pygame
import config
from Container      import Container
from LayoutManagers import FlowLayout

class Panel(Container):
    """
    """

    def __init__(self, left=0, top=0, width=0, height=0, bg_color=None, 
                 fg_color=None, border=None, bd_color=None, bd_width=None):

        Container.__init__(self, left, top, width, height, bg_color, fg_color,
                           border, bd_color, bd_width)

        self.h_margin = 0
        self.v_margin = 0


    def set_parent(self, parent):
        Container.set_parent(self, parent)

        if self.parent:
            if isinstance(self.parent.get_layout(), FlowLayout):
                self.width = self.parent.width - 2 * self.parent.h_margin


    def _draw(self):
        # leaving comments in until done debugging
        # self.surface = self.parent.surface.subsurface((0,0,self.width,self.height))
        self.surface = self.parent.surface.subsurface((self.left,self.top,self.width,self.height))

        #self.surface = pygame.Surface(self.get_size(), 0, 32)
        ## self.surface.fill(None)
        #self.surface.set_alpha(255)

        Container._draw(self)

        self.blit_parent()
