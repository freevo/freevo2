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
# Revision 1.11  2003/06/07 11:31:07  dischi
# bugfix
#
# Revision 1.10  2003/05/27 17:53:34  dischi
# Added new event handler module
#
# Revision 1.9  2003/05/21 00:01:31  rshortt
# Contructors may now accept a handler method to call when ok/enter is selected.
#
# Revision 1.8  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.7  2003/04/24 19:56:20  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.6  2003/04/20 13:02:29  dischi
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
# Revision 1.1  2003/02/18 13:40:52  rshortt
# Reviving the src/gui code, allso adding some new GUI objects.  Event
# handling will not work untill I make some minor modifications to main.py,
# osd.py, and menu.py.
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

import event as em

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

        
    def __init__(self, parent='osd', text=" ", handler=None, left=None, top=None, 
                 width=300, height=160, bg_color=None, fg_color=None, icon=None,
                 border=None, bd_color=None, bd_width=None):

        PopupBox.__init__(self, parent, text, handler, left, top, width, height, 
                          bg_color, fg_color, icon, border, bd_color, bd_width)

        self.lbg = LetterBoxGroup()
        self.add_child(self.lbg)


    def eventhandler(self, event):
        
        if event == em.INPUT_LEFT:
            self.lbg.change_selected_box('left')
            self.draw()
            self.osd.update(self.get_rect())

        elif event == em.INPUT_RIGHT:
            self.lbg.change_selected_box('right')
            self.draw()
            self.osd.update(self.get_rect())

        elif event == em.INPUT_ENTER:
            self.destroy()
            if self.handler: self.handler(self.lbg.get_word())

        elif event == em.INPUT_EXIT:
            self.destroy()

        elif event == em.INPUT_UP:
            self.lbg.get_selected_box().charUp()
            self.draw()
            self.osd.update(self.get_rect())

        elif event == em.INPUT_DOWN:
            self.lbg.get_selected_box().charDown()
            self.draw()
            self.osd.update(self.get_rect())

        elif event in (em.INPUT_0, em.INPUT_1, em.INPUT_2, em.INPUT_3,
                       em.INPUT_4, em.INPUT_5, em.INPUT_6, em.INPUT_7,
                       em.INPUT_8, em.INPUT_9, em.INPUT_0 ):
            self.lbg.get_selected_box().cycle_phone_char(event.arg)
            self.draw()
            self.osd.update(self.get_rect())
            # a,b,c,d = self.lbg.get_selected_box().get_rect()
            # print 'rectangle: %s' % dir(self.lbg.get_selected_box().get_rect())
            # if DEBUG: print 'a: "%s", b: "%s", c: "%s", d: "%s"' % (a,b,c,d)
            # self.osd.update_area(self.lbg.get_selected_box().get_rect())

        else:
            return self.parent.eventhandler(event)

