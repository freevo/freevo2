# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Label - A class for text labels
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/10/03 15:54:00  dischi
# make PopupBoxes work again as they should
#
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

import math

import config
import gui

from textbox import Textbox

class Label(Textbox):
    """
    """
    
    def __init__(self, text, pos, size, style, align_h=None, align_v=None, 
                 width=-1, height=-1, text_prop=None, scale=False):

        self.text_prop = text_prop or { 'align_h': 'left',
                                        'align_v': 'top',
                                        'mode'   : 'hard',
                                        'hfill'  : False }

        self.style = style

        if scale:
            # We need at least text_height * text_width space for the text, in
            # most cases more (because of line breaks. To make the text look
            # nice, we try 4:3 aspect of the box at first and than use the max
            # height we can get
            text_width  = style.font.stringsize(text)
            text_height = int(style.font.height * 1.2)
            w = max(min(int(math.sqrt(text_height * text_width * 4 / 3)),
                        gui.get_display().width - 60 - \
                        2 * config.OSD_OVERSCAN_X), size[0])
            h = gui.get_display().height - 100 - 2 * config.OSD_OVERSCAN_Y
            size = w, h
            
        self.align_h = align_h or self.text_prop.setdefault( 'align_h', 'left' )
        self.align_v = align_v or self.text_prop.setdefault( 'align_v', 'top' )

        mode = self.text_prop.setdefault( 'mode', 'hard' )

        Textbox.__init__(self, text, pos, size, style.font, align_h, align_v, mode)
