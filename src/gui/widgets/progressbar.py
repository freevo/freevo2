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
# Revision 1.3  2004/10/04 18:37:20  dischi
# make ProgressBox work again
#
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


from mevas.image import CanvasImage
from rectangle import Rectangle

class Progressbar(CanvasImage):
    """
    """
    def __init__(self, pos, size, full, style):
        CanvasImage.__init__(self, size)
        self.set_pos(pos)

        self.bar_position = 0
        self.full = full
        self.style = style
        self._draw()
        

    def _draw(self):
        self.draw_rectangle((0,0), self.get_size(), (0,0,0,0), 1)
        r = self.style.rectangle
        self.draw_image(Rectangle((0,0), self.get_size(), None, r.size, r.color, r.radius))

        # catch division by zero error.
        if not self.full:
            return
        
        position = min((self.bar_position * 100) / self.full, 100)

        width = ((self.get_size()[0]) * position ) / 100
        if width > r.size * 2:
            self.draw_image(Rectangle((0,0), (width, self.get_size()[1]),
                                      r.bgcolor, r.size, r.color, r.radius))


    def tick(self):
        if self.bar_position < self.full:
            self.bar_position += 1
        self._draw()

