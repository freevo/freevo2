# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# progressbar.py - a simple progress bar
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/27 18:52:31  dischi
# support more layer (see README.txt in backends for details
#
# Revision 1.1  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
#
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


from base import GUIObject

class Progressbar(GUIObject):
    """
    """

    def __init__(self, x1, y1, x2, y2, full, style):
        
        GUIObject.__init__(self, x1, y1, x2, y2)

        self.bar_position = 0
        self.full         = full
        self.style        = style


    def draw(self, rect=None):
        if not self.screen:
            raise TypeError, 'no screen defined for %s' % self

        r = self.style.rectangle
        self.screen.drawbox(self.x1, self.y1, self.x2, self.y2,
                            color=0xaa000000, border_size=r.size,
                            border_color=r.color, radius=r.radius)

        # catch division by zero error.
        if not self.full:
            return
        
        position = min((self.bar_position * 100) / self.full, 100)

        width = ((self.x2 - self.x1) * position ) / 100
        if width > r.size * 2:
            self.screen.drawbox(self.x1, self.y1, self.x1 + width, self.y2,
                                color=r.bgcolor, border_size=r.size,
                                border_color=r.color, radius=r.radius)

    def tick(self):
        if self.bar_position < self.full:
            self.bar_position += 1
        self.modified()

