#if 0 /*
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
# Revision 1.1  2003/09/01 18:52:55  dischi
# Add progressbar and box with progressbar
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
#endif
import config

from GUIObject   import *
from PopupBox    import *
from Color       import *
from Progressbar import *
from Border      import *
from Label       import *
from types       import *

DEBUG = 0

import event as em

class ProgressBox(PopupBox):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    icon      icon
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    def __init__(self, parent='osd', text=" ", left=None, 
                 top=None, width=0, height=0, bg_color=None, fg_color=None,
                 icon=None, border=None, bd_color=None, bd_width=None,
                 vertical_expansion=1, full=0):

        PopupBox.__init__(self, parent, text, None, left, top, width, height,
                          bg_color, fg_color, icon, border, bd_color, bd_width,
                          vertical_expansion)

        self.progressbar = Progressbar(full=full, width=self.width-20)
        self.add_child(self.progressbar)


    def tick(self):
        self.progressbar.tick()
        self.draw()
        self.osd.update(self.get_rect())

        
    def eventhandler(self, event):
        return self.parent.eventhandler(event)


