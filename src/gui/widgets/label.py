# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Label - A class for text labels
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


from text import Text

class Label(Text):
    """
    """
    
    def __init__(self, x1, y1, x2, y2, text, style, align_h=None, align_v=None, 
                 width=-1, height=-1, text_prop=None):

        self.text_prop = text_prop or { 'align_h': 'left',
                                        'align_v': 'top',
                                        'mode'   : 'hard',
                                        'hfill'  : False }

        self.style = style
        
        self.align_h = align_h or self.text_prop.setdefault( 'align_h', 'left' )
        self.align_v = align_v or self.text_prop.setdefault( 'align_v', 'top' )

        mode = self.text_prop.setdefault( 'mode', 'hard' )

        Text.__init__(self, x1, y1, x2, y2, text, style.font,
                      y2 - y1, align_h, align_v, mode)

        rect = self.calculate()[1]

        self.x1 = rect[0]
        self.y1 = rect[1]
        self.x2 = rect[2]
        self.y2 = rect[3]

        self.height = self.y2 - self.y1
        self.width  = self.x2 - self.x1


    def set_style(self, style):
        self.style = style
        self.font  = style.font
        self.modified()
        

    def set_text(self, text):
        self.text = text
        self.modified()
        

    def set_position(self, x1, y1, x2, y2):
        """
        change the position (will be done by the layer)
        """
        Text.set_position(self, x1, y1, x2, y2)
        self.modified()
