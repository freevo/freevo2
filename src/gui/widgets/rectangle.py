# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# rectangle.py - basic rectangle widget
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/08/01 10:37:08  dischi
# smaller changes to stuff I need
#
# Revision 1.2  2004/07/27 18:52:31  dischi
# support more layer (see README.txt in backends for details
#
# Revision 1.1  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
#
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


from base import GUIObject

class Rectangle(GUIObject):
    """
    A rectangle object that can be drawn onto a layer
    """
    def __init__(self, x1, y1, x2, y2, bgcolor, size, color, radius):
        GUIObject.__init__(self, x1, y1, x2, y2)
        self.bgcolor = bgcolor
        self.size    = size
        self.color   = color
        self.radius  = radius


    def draw(self, rect=None):
        if not self.screen:
            raise TypeError, 'no screen defined for %s' % self
        self.screen.drawbox(self.x1, self.y1, self.x2, self.y2, color=self.bgcolor,
                            border_size=self.size, border_color=self.color,
                            radius=self.radius, force_alpha=self.layer>= 0)

            
    def __cmp__(self, o):
        try:
            return self.x1 != o.x1 or self.y1 != o.y1 or self.x2 != o.x2 or \
                   self.y2 != o.y2 or self.bgcolor != o.bgcolor or \
                   self.size != o.size or self.color != o.color or self.radius != o.radius
        except:
            return 1
    
