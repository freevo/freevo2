# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# AlertBox.py - simple alert popup box class
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/25 18:14:04  dischi
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


from event import *

from PopupBox  import PopupBox
from button    import Button


class AlertBox(PopupBox):
    """
    """

    def __init__(self, text, handler=None, x=None, y=None, width=None, height=None,
                 icon=None, vertical_expansion=1, text_prop=None):

        PopupBox.__init__(self, text, handler, x, y, width, height,
                          icon, vertical_expansion, text_prop)

        self.button = Button(self.x1, self.y1, self.x2, self.y2, _('OK'),
                             self.button_selected)
        self.add(self.button)

        # FIXME: that can't be correct
        space = self.content_layout.spacing * 2

        # get height of the button and set it to set bottom
        ydiff = self.button.y2 - (self.y2 - space)
        bx1   = min(self.x1 + space, self.button.x1)
        bx2   = max(self.x2 - space, self.button.x2)

        self.button.set_position(bx1, self.button.y1 - ydiff, bx2, self.button.y2 - ydiff)

        # resize label to fill the rest of the box
        self.label.set_position(self.x1 + space, self.y1 + space, self.x2 - space,
                                self.y2 - space + ydiff - space)
        

        
    def eventhandler(self, event):
        if event in (INPUT_ENTER, INPUT_EXIT):
            self.destroy()
            if self.handler:
                self.handler()
        else:
            return self.parent_handler(event)
