# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# ProgressBox.py - simple box with progress bar
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/25 18:14:05  dischi
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

from PopupBox import PopupBox
from progressbar import Progressbar

class ProgressBox(PopupBox):
    """
    """
    def __init__(self, text, x=None, y=None, width=None, height=None,
                 icon=None, vertical_expansion=1, text_prop=None,
                 full=0):

        PopupBox.__init__(self, text, None, x, y, width, height,
                          icon, vertical_expansion, text_prop)

        # FIXME: that can't be correct
        space = self.content_layout.spacing * 2

        self.bar = Progressbar(self.x1 + space, self.y2 - 2 * space, self.x2 - space,
                               self.y2 - space, full, self.widget_normal)
        self.add(self.bar)

        # resize label to fill the rest of the box
        self.label.set_position(self.x1 + space, self.y1 + space,
                                self.x2 - space, self.y2 - 3 * space)



    def tick(self):
        self.bar.tick()
        self.screen.update()
