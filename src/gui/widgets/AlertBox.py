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
# Revision 1.6  2004/10/04 18:37:48  dischi
# fix to changed PopupBox __init__
#
# Revision 1.5  2004/10/03 15:54:00  dischi
# make PopupBoxes work again as they should
#
# Revision 1.4  2004/08/24 16:42:42  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.3  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.2  2004/07/25 18:14:04  dischi
# make some widgets and boxes work with the new gui interface
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


from event import *

from PopupBox  import PopupBox
from button    import Button


class AlertBox(PopupBox):
    """
    """

    def __init__(self, text, handler=None):
        PopupBox.__init__(self, text)
        self.handler = handler
        c = self.content_pos

        self.button = Button(_('OK'), (c.x1, c.y1), self.get_size()[0] - c.width,
                             self.button_selected)
        y = self.add_row(self.button.get_size()[1])
        self.button.set_pos((self.button.get_pos()[0], y))
        self.add_child(self.button)
        

    def eventhandler(self, event):
        if event in (INPUT_ENTER, INPUT_EXIT):
            self.destroy()
            if self.handler:
                self.handler()
