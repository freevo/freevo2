#if 0 /*
# -----------------------------------------------------------------------
# InputBox.py - a popup box that has a message and allows the user
#               to input using the remote control
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
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
# Revision 1.1  2003/02/18 13:40:52  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
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

from GUIObject      import *
from PopupBox       import *
from Color          import *
from Button         import *
from Border         import *
from Label          import *
from LetterBoxGroup import *
from types          import *

DEBUG = 0


class InputBox(PopupBox):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    handler   Function to call after pressing ENTER.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    icon      icon
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

        
    def __init__(self, text=" ", handler=None, left=None, top=None, 
                 width=300, height=160, bg_color=None, fg_color=None, 
                 icon=None, border=None, bd_color=None, bd_width=None):

        self.handler = handler

        PopupBox.__init__(self, text, left, top, width, height, bg_color, 
                          fg_color, icon, border, bd_color, bd_width)


        self.set_v_align(Align.NONE)
        self.set_h_align(Align.CENTER)

        self.label.top = self.top + 25

        self.lbg = LetterBoxGroup()
        bleft = self.left + self.width/2 - self.lbg.width/2
        btop = self.top + self.height - self.lbg.height - 25
        self.lbg.set_position(bleft, btop) 
        self.add_child(self.lbg)


    def eventhandler(self, event):

        if event == self.rc.LEFT:
            self.lbg.change_selected_box('left')
            self.lbg.draw()
            self.osd.update(self.lbg.get_rect())
            return
        elif event == self.rc.RIGHT:
            self.lbg.change_selected_box('right')
            self.lbg.draw()
            self.osd.update(self.lbg.get_rect())
            return
        elif event == self.rc.ENTER or event == self.rc.SELECT:
            self.destroy()
            if self.handler: self.handler(self.lbg.get_word())
            return
        elif event == self.rc.EXIT:
            self.destroy()
            return
        elif event == self.rc.UP:
            self.lbg.get_selected_box().charUp()
            self.lbg.draw()
            self.osd.update(self.lbg.get_rect())
            return
        elif event == self.rc.DOWN:
            self.lbg.get_selected_box().charDown()
            self.lbg.draw()
            self.osd.update(self.lbg.get_rect())
            return
        elif [self.rc.K1, self.rc.K2, self.rc.K3, self.rc.K4, self.rc.K5, 
              self.rc.K6, self.rc.K7, self.rc.K8, self.rc.K9, 
              self.rc.K0].count(event) > 0:
            self.lbg.get_selected_box().cycle_phone_char(event)
            self.lbg.draw()
            self.osd.update(self.lbg.get_rect())
            # a,b,c,d = self.lbg.get_selected_box().get_rect()
            # print 'rectangle: %s' % dir(self.lbg.get_selected_box().get_rect())
            # if DEBUG: print 'a: "%s", b: "%s", c: "%s", d: "%s"' % (a,b,c,d)
            # self.osd.update_area(self.lbg.get_selected_box().get_rect())
            return
        else:
            return self.parent.eventhandler(event)

