#if 0 /*
# -----------------------------------------------------------------------
# scrolldemo.py - lets demonstrate scrolling capabilities
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/05/02 01:09:03  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.7  2003/04/24 19:56:31  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.6  2003/04/20 13:02:30  dischi
# make the rc changes here, too
#
# Revision 1.5  2003/03/30 15:54:07  rshortt
# Added 'parent' as a constructor argument for PopupBox and all of its
# derivatives.
#
# Revision 1.4  2003/03/09 21:37:06  rshortt
# Improved drawing.  draw() should now be called instead of _draw(). draw()
# will check to see if the object is visible as well as replace its bg_surface
# befire drawing if it is available which will make transparencies redraw
# correctly instead of having the colour darken on every draw.
#
# Revision 1.3  2003/03/05 03:53:34  rshortt
# More work hooking skin properties into the GUI objects, and also making
# better use of OOP.
#
# ListBox and others are working again, although I have a nasty bug regarding
# alpha transparencies and the new skin.
#
# Revision 1.2  2003/02/24 12:14:57  rshortt
# Removed more unneeded self.parent.refresh() calls.
#
# Revision 1.1  2003/02/19 00:58:18  rshortt
# Added scrolldemo.py for a better demonstration.  Use my audioitem.py
# to test.
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

from GUIObject      import *
from PopupBox       import *
from RegionScroller import *
from Color          import *
from Button         import *
from Border         import *
from Label          import *
from types          import *

import rc

DEBUG = 0


class scrolldemo(PopupBox):
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

    def __init__(self, parent='osd', text=' ', left=None, top=None, width=500, 
                 height=350, bg_color=None, fg_color=None, icon=None,
                 border=None, bd_color=None, bd_width=None):

        PopupBox.__init__(self, parent, text, left, top, width, height, 
                          bg_color, fg_color, icon, border, bd_color, bd_width)


        self.set_h_align(Align.CENTER)

        surf = self.osd.getsurface(0, 0, 700, 500)
        self.pb = RegionScroller(surf, 50,50, width=450, height=250)
        self.add_child(self.pb)


    def eventhandler(self, event):

        scrolldirs = [rc.UP, rc.DOWN, rc.LEFT, rc.RIGHT]
        if scrolldirs.count(event) > 0:
            return self.pb.eventhandler(event)
        elif event == rc.ENTER or event == rc.SELECT or event == rc.EXIT:
            self.destroy()
        else:
            return self.parent.eventhandler(event)


