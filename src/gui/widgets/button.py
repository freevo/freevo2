# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Button.py - a simple button class
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


from label import Label

class Button(Label):
    """
    """
    def __init__(self, x1, y1, x2, y2, text, style):
        Label.__init__(self, x1, y1, x2, y2, text, style, 'center', 'center')

        # enhance the space for the button to fit the border
        self.x1 -= 10
        self.y1 -= 2
        self.x2 += 10
        self.y2 += 2
        self.height += 4
        self.width  += 10
        

    def draw(self, rect=None):
        self.screen.drawbox(self.x1, self.y1, self.x2, self.y2,
                            color=self.style.rectangle.bgcolor,
                            border_size=self.style.rectangle.size,
                            border_color=self.style.rectangle.color,
                            radius=self.style.rectangle.radius)
        Label.draw(self, rect)
