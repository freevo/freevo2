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
# Revision 1.14  2004/02/18 21:52:04  dischi
# Major GUI update:
# o started converting left/right to x/y
# o added Window class as basic for all popup windows which respects the
#   skin settings for background
# o cleanup on the rendering, not finished right now
# o removed unneeded files/functions/variables/parameter
# o added special button skin settings
#
# Some parts of Freevo may be broken now, please report it to be fixed
#
# Revision 1.13  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.12  2003/09/06 13:29:00  gsbarbieri
# PopupBox and derivates now support you to choose mode (soft/hard) and
# alignment (vertical/horizontal).
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
from event import *

from GUIObject      import *
from PopupBox       import *
from LetterBoxGroup import *


class InputBox(PopupBox):
    """
    x         x coordinate. Integer
    y         y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    icon      icon
    text_prop A dict of 3 elements composing text proprieties:
              { 'align_h' : align_h, 'align_v' : align_v, 'mode' : mode }
                 align_v = text vertical alignment
                 align_h = text horizontal alignment
                 mode    = hard (break at chars); soft (break at words)
    """

    def __init__(self, text, handler=None, x=None, y=None, width=0, height=0,
                 icon=None, vertical_expansion=1, text_prop=None, parent='osd'):

        PopupBox.__init__(self, text, handler, x, y, width, height,
                          icon, vertical_expansion, text_prop, parent)

        self.lbg = LetterBoxGroup()
        self.add_child(self.lbg)


    def eventhandler(self, event):
        
        if event == INPUT_LEFT:
            self.lbg.change_selected_box('left')
            self.draw(update=True)

        elif event == INPUT_RIGHT:
            self.lbg.change_selected_box('right')
            self.draw(update=True)

        elif event == INPUT_ENTER:
            self.destroy()
            if self.handler: self.handler(self.lbg.get_word())

        elif event == INPUT_EXIT:
            self.destroy()

        elif event == INPUT_UP:
            self.lbg.get_selected_box().charUp()
            self.draw(update=True)

        elif event == INPUT_DOWN:
            self.lbg.get_selected_box().charDown()
            self.draw(update=True)

        elif event in (INPUT_0, INPUT_1, INPUT_2, INPUT_3,
                       INPUT_4, INPUT_5, INPUT_6, INPUT_7,
                       INPUT_8, INPUT_9, INPUT_0 ):
            self.lbg.get_selected_box().cycle_phone_char(event.arg)
            self.draw(update=True)
        else:
            return self.parent.eventhandler(event)

