# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Label - A class for text labels
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
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


from text import Text

class Label(Text):
    """
    """
    
    def __init__(self, text, pos, size, style, align_h=None, align_v=None, 
                 width=-1, height=-1, text_prop=None):

        self.text_prop = text_prop or { 'align_h': 'left',
                                        'align_v': 'top',
                                        'mode'   : 'hard',
                                        'hfill'  : False }

        self.style = style
        
        self.align_h = align_h or self.text_prop.setdefault( 'align_h', 'left' )
        self.align_v = align_v or self.text_prop.setdefault( 'align_v', 'top' )

        mode = self.text_prop.setdefault( 'mode', 'hard' )

        Text.__init__(self, text, pos, size, style.font,
                      align_h, align_v, mode)
