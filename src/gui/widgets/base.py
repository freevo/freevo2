# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# GUIObject - Common object for all GUI Classes
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
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

class GUIObject:
    """
    Common parent class of all GUI objects. You can override this to make
    new Widgets.
    """
    def __init__(self, x1, y1, x2, y2):
        """
        set basic information for a gui object
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.width    = x2 - x1
        self.height   = y2 - y1
        self.layer    = None
        self.position = 0


    def draw(self, rect=None):
        """
        The drawing should take place here
        """
        pass

    
    def set_position(self, x1, y1, x2, y2):
        """
        change the position (will be done by the layer)
        """
        if self.layer:
            self.layer.set_position(self, x1, y1, x2, y2)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.width    = x2 - x1
        self.height = y2 - y1
        
            
    def modified(self):
        """
        call this function to notify the layer that this object
        needs a redraw
        """
        if self.layer:
            self.layer.modified(self)
            

