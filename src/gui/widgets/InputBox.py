# -*- coding: iso-8859-1 -*-
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
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.19  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.18  2004/03/19 21:11:17  dischi
# fix input return handling
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
    type      'normal' or 'password'
    icon      icon
    text_prop A dict of 4 elements composing text proprieties:
              { 'align_h' : align_h, 'align_v' : align_v, 'mode' : mode, 'hfill': hfill }
                 align_v = text vertical alignment
                 align_h = text horizontal alignment
                 mode    = hard (break at chars); soft (break at words)
                 hfill   = True (don't shorten width) or False
    """

    def __init__(self, text, handler=None, type='text', x=None, y=None, width=0, height=0,
                 icon=None, vertical_expansion=1, text_prop=None, input_text='',
                 numboxes=0, parent='osd'):

        PopupBox.__init__(self, text, handler, x, y, width, height,
                          icon, vertical_expansion, text_prop, parent)

        self.lbg = LetterBoxGroup(type=type, numboxes=numboxes, text=input_text,
                                  width=self.content.width-self.content.h_margin*2)
        self.add_child(self.lbg)
        

    def eventhandler(self, event):
        if self.lbg.eventhandler(event):
            self.draw()
            return True
        
        if event == INPUT_ENTER:
            txt = self.lbg.get_word()
            self.destroy()
            if self.handler:
                self.handler(txt)
            return True

        if event == INPUT_EXIT:
            self.destroy()
            return True

        return self.parent.eventhandler(event)
