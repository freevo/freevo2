#if 0 /*
# -----------------------------------------------------------------------
# optiondemo.py - lets demonstrate the option box
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.11  2003/07/13 19:28:58  rshortt
# Bugfix.
#
# Revision 1.10  2003/05/27 17:53:34  dischi
# Added new event handler module
#
# Revision 1.9  2003/05/21 00:02:47  rshortt
# Updates for changes elsewhere.
#
# Revision 1.8  2003/05/15 02:21:54  rshortt
# got RegionScroller, ListBox, ListItem, OptionBox working again, although
# they suffer from the same label alignment bouncing bug as everything else
#
# Revision 1.7  2003/04/24 19:56:30  dischi
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
# Revision 1.2  2003/02/24 12:10:24  rshortt
# Fixed a bug where a popup would reapear after it was disposed of since its
# parent would redraw it before it completely left.
#
# Revision 1.1  2003/02/24 11:58:28  rshortt
# Adding OptionBox and optiondemo.  Also some minor cleaning in a few other
# objects.
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
from OptionBox      import *
from ListItem       import *
from Color          import *
from Button         import *
from Border         import *
from Label          import *
from types          import *

import event as em

class optiondemo(PopupBox):
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

    def __init__(self, parent=None, text=" ", left=None, top=None, width=500, 
                 height=350, bg_color=None, fg_color=None, icon=None,
                 border=None, bd_color=None, bd_width=None):

        handler = None

        PopupBox.__init__(self, parent, text, handler, left, top, width, height, 
                          bg_color, fg_color, icon, border, bd_color, bd_width)


        # self.label.top = self.top + 25

        self.ob = OptionBox('Default')
        self.ob.set_h_align(Align.CENTER)
        self.ob.set_v_align(Align.CENTER)
      
        for i in range(20):
            iname = "Item %s" % i
            self.ob.add_item(text=iname, value=i)

        self.ob.toggle_selected_index(0)
        self.ob.toggle_selected()
        self.add_child(self.ob)
        # print 'CP: %s,%s' % self.ob.calc_position()
        # self.ob.set_position(self.ob.calc_position())
        # self.ob.set_position(371, 275)


    def eventhandler(self, event):

        if event in (em.INPUT_UP, em.INPUT_DOWN, em.INPUT_LEFT, em.INPUT_RIGHT ):
            self.ob.change_item(event)
            self.draw()

        elif event == em.INPUT_ENTER:
            if self.ob.selected or self.ob.list.is_visible():
                print '  Want to toggle_box'
                self.ob.toggle_box()
                self.draw()

        elif event == em.INPUT_EXIT:
            self.destroy()

        else:
            return self.parent.eventhandler(event)

        self.osd.update(self.get_rect())


