#if 0 /*
# -----------------------------------------------------------------------
# ConfirmBox.py - a popup box that asks a question and prompts
#                 for ok/cancel
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.17  2003/07/20 09:46:11  dischi
# Some default width fixes to match the current new default font. It would
# be great if a box without width and height could be as big as needed
# automaticly (with a max width). Right now, the buttons in the ConfirmBox
# are not at the bottom of the box, that should be fixed.
#
# Revision 1.16  2003/06/25 02:27:39  rshortt
# Allow 'frame' containers to grow verticly to hold all contents.  Also
# better control of object's background images.
#
# Revision 1.15  2003/05/27 17:53:34  dischi
# Added new event handler module
#
# Revision 1.14  2003/05/21 00:01:31  rshortt
# Contructors may now accept a handler method to call when ok/enter is selected.
#
# Revision 1.13  2003/05/04 23:18:19  rshortt
# Change some height values (temporarily) to avoid some crashes.
#
# Revision 1.12  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.11  2003/04/24 19:56:18  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.10  2003/04/20 13:02:29  dischi
# make the rc changes here, too
#
# Revision 1.9  2003/04/13 17:50:12  dischi
# fixed crash by setting the default parent
#
# Revision 1.8  2003/03/30 20:49:59  rshortt
# Improvements in how we get skin properties.
#
# Revision 1.7  2003/03/30 15:54:07  rshortt
# Added 'parent' as a constructor argument for PopupBox and all of its
# derivatives.
#
# Revision 1.6  2003/03/24 01:53:15  rshortt
# Added support in the contructor to have either button selected by
# default instead of assuming 'OK' to be the default all the time.
#
# Revision 1.5  2003/03/23 23:11:10  rshortt
# Better default height now.
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

from GUIObject import *
from PopupBox  import *
from Color     import *
from Button    import *
from Border    import *
from Label     import *
from types     import *

DEBUG = 0

import event as em

class ConfirmBox(PopupBox):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    handler   Function to call when 'OK' is hit
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    icon      icon
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    def __init__(self, parent='osd', text=" ", handler=None, default_choice=0, 
                 left=None, top=None, width=400, height=150, bg_color=None, 
                 fg_color=None, icon=None, border=None, bd_color=None, 
                 bd_width=None, vertical_expansion=1):

        PopupBox.__init__(self, parent, text, handler, left, top, width, height, 
                          bg_color, fg_color, icon, border, bd_color, bd_width,
                          vertical_expansion)


        # XXX: It may be nice if we could choose between
        #      OK/CANCEL and YES/NO

        self.b0 = Button('OK', width=(width-60)/2)
        self.b0.set_h_align(Align.NONE)
        self.add_child(self.b0)

        self.b1 = Button('CANCEL', width=(width-60)/2)
        self.b1.set_h_align(Align.NONE)
        self.add_child(self.b1)
        select = 'self.b%s.toggle_selected()' % default_choice
        eval(select)


    def eventhandler(self, event):
        if DEBUG: print 'ConfirmBox: EVENT = %s' % event

        if event in (em.INPUT_LEFT, em.INPUT_RIGHT):
            self.b0.toggle_selected()
            self.b1.toggle_selected()
            self.draw()
            self.osd.update(self.get_rect())
            return
        
        elif event == em.INPUT_ENTER:
            if self.b0.selected:
                if DEBUG: print 'HIT OK'
                self.destroy()
                if self.handler: self.handler()
            else:
                self.destroy()

        else:
            return self.parent.eventhandler(event)


