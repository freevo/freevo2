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
# Revision 1.1  2004/07/22 21:12:35  dischi
# move all widget into subdir, code needs update later
#
# Revision 1.23  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.22  2004/02/24 18:56:09  dischi
# add hfill to text_prop
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

from GUIObject import *
from PopupBox  import *
from Button    import *


class AlertBox(PopupBox):
    """
    x         x coordinate. Integer
    y         y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    icon      icon
    text_prop A dict of 4 elements composing text proprieties:
              { 'align_h' : align_h, 'align_v' : align_v, 'mode' : mode, 'hfill': hfill }
                 align_v = text vertical alignment
                 align_h = text horizontal alignment
                 mode    = hard (break at chars); soft (break at words)
                 hfill   = True (don't shorten width) or False
    """

    def __init__(self, text, handler=None, x=None, y=None, width=0, height=0,
                 icon=None, vertical_expansion=1, text_prop=None, parent='osd'):

        PopupBox.__init__(self, text, handler, x, y, width, height,
                          icon, vertical_expansion, text_prop, parent)

        b1 = Button(_('OK'))
        b1.toggle_selected()

        self.add_child(b1)


    def eventhandler(self, event):
        if event in (INPUT_ENTER, INPUT_EXIT):
            self.destroy()
            if self.handler:
                self.handler()
        else:
            return self.parent.eventhandler(event)
