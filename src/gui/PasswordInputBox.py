#if 0 /*
# ------------------------------------------------------------------------
# PasswordInputBox.py - a popup box that has a message and allows the user
#                       to input a password using the remote control
# ------------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/04/24 19:56:26  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.3  2003/04/21 12:57:41  dischi
# make osd.focusapp default parent
#
# Revision 1.2  2003/04/20 13:02:29  dischi
# make the rc changes here, too
#
# Revision 1.1  2003/03/30 17:21:20  rshortt
# New classes: PasswordInputBox, PasswordLetterBox.
# PasswordLetterBox is a subclass of Letterbox, PasswordInputBox does not
# extend InputBox but instead is also a subclass of PopupBox.  LetterBoxGroup
# has a new constructor argument called 'type' which when set to 'password'
# will make a LetterBoxGroup of PasswordLetterBox's rather than Letterbox's.
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

import rc

DEBUG = 0


class PasswordInputBox(PopupBox):
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

        if parent:
            self.parent = parent
            
        self.handler = handler

        PopupBox.__init__(self, parent, text, left, top, width, height, 
                          bg_color, fg_color, icon, border, bd_color, bd_width)


        self.set_v_align(Align.NONE)
        self.set_h_align(Align.CENTER)

        self.label.top = self.top + 25

        self.lbg = LetterBoxGroup(type='password')
        bleft = self.left + self.width/2 - self.lbg.width/2
        btop = self.top + self.height - self.lbg.height - 25
        self.lbg.set_position(bleft, btop) 
        self.add_child(self.lbg)


    def eventhandler(self, event):

        if event == rc.LEFT or event == rc.UP:
            self.lbg.change_selected_box('left')
            self.lbg.draw()
            self.osd.update(self.lbg.get_rect())
            return
        elif event == rc.RIGHT or event == rc.DOWN:
            self.lbg.change_selected_box('right')
            self.lbg.draw()
            self.osd.update(self.lbg.get_rect())
            return
        elif event == rc.ENTER or event == rc.SELECT:
            self.destroy()
            if self.handler: self.handler(self.lbg.get_word())
            return
        elif event == rc.EXIT:
            self.destroy()
            return
        elif [rc.K1, rc.K2, rc.K3, rc.K4, rc.K5, 
              rc.K6, rc.K7, rc.K8, rc.K9, 
              rc.K0].count(event) > 0:
            the_box = self.lbg.get_selected_box()
            the_box.cycle_phone_char(event)
            if self.lbg.boxes.index(the_box) != len(self.lbg.boxes)-1:
                self.lbg.change_selected_box('right')
            self.lbg.draw()
            self.osd.update(self.lbg.get_rect())
            return
        else:
            return self.parent.eventhandler(event)

