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
# Revision 1.3  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
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


from label import Label
from rectangle import Rectangle
from mevas.image import CanvasImage

class Button(CanvasImage):
    """
    """
    def __init__(self, text, pos, width, style):
        label = Label(text, (0,0), (width - 20, style.font.height), style, 'center', 'center')
        CanvasImage.__init__(self, (width, style.font.height+4))

        r = Rectangle((0,0), self.get_size(),
                      style.rectangle.bgcolor,
                      style.rectangle.size,
                      style.rectangle.color,
                      style.rectangle.radius)
        self.draw_image(r, (0, 0))
        self.draw_image(label, ((width - label.get_size()[0]) / 2, 2))
        self.set_pos(pos)
