# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# progressbar.py - a simple progress bar
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:     o remove theme style dep
#           o support 'set to position'
#           o support 'set percent'
#           o doc
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2005/06/26 17:04:19  dischi
# adjust to mevas - kaa.mevas move
#
# Revision 1.6  2004/10/30 18:46:33  dischi
# only redraw when needed, fix typo
#
# Revision 1.5  2004/10/09 16:21:29  dischi
# make Progessbar not depend on popup box settings
#
# Revision 1.4  2004/10/05 19:50:55  dischi
# Cleanup gui/widgets:
# o remove unneeded widgets
# o move window and boxes to the gui main level
# o merge all popup boxes into one file
# o rename popup boxes
#
# Revision 1.3  2004/10/04 18:37:20  dischi
# make ProgressBox work again
#
# Revision 1.2  2004/07/27 18:52:31  dischi
# support more layer (see README.txt in backends for details
#
# Revision 1.1  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
# Please see the file doc/CREDITS for a complete list of authors.
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


from kaa.mevas.container import CanvasContainer
from rectangle import Rectangle

class Progressbar(CanvasContainer):
    """
    """
    def __init__(self, pos, size, border_size, border_color, bgcolor, bar_size,
                 bar_color, bar_bgcolor, radius, max_value):
        CanvasContainer.__init__(self)
        self.set_pos(pos)

        self.bar_position = 0
        self.max_value   = max_value
        self.border_size = border_size
        self.bar_size    = bar_size
        self.bar_color   = bar_color
        self.bar_bgcolor = bar_bgcolor
        self.radius      = radius
        self.bar         = None
        
        rect = Rectangle((0,0), size, bgcolor, border_size, border_color,
                         self.radius)
        self.add_child(rect)
        self.__last_position = None
        self.__draw()
        

    def __draw(self):
        # catch division by zero error.
        if not self.max_value:
            return

        position = min((self.bar_position * 100) / self.max_value, 100)
        width = ((self.get_size()[0]) * position ) / 100

        if self.__last_position == width:
            return
        self.__last_position = width

        if self.bar:
            self.remove_child(self.bar)
            
        if width > self.border_size * 2:
            rect = Rectangle((self.border_size,self.border_size),
                             (width-self.border_size*2,
                              self.get_size()[1]-self.border_size*2),
                             self.bar_bgcolor, self.bar_size, self.bar_color,
                             self.radius)
            self.add_child(rect)
            self.bar = rect


    def tick(self):
        if self.bar_position < self.max_value:
            self.bar_position += 1
        self.__draw()


    def set_max_value(self, max_value):
        self.max_value = max_value
        self.__draw()


    def set_bar_position(self, position):
        self.bar_position = position
        self.__draw()
        
