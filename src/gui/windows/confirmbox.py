# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# confirmbox.py - a box with Yes/No buttons
# -----------------------------------------------------------------------------
# $Id$
#
# A box with two buttons: Yes and No. It can have additional handles what
# function should be called if Yes is selected. INPUT_EXIT will be close
# the box like pressing No.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
# -----------------------------------------------------------------------------

__all__ = [ 'ConfirmBox' ]

# python imports
import logging

# freevo imports
from event import *

# gui imports
from gui.widgets.textbox import Textbox
from gui.widgets.button import Button

# windows imports
from waitbox import WaitBox

# get logging object
log = logging.getLogger()


class ConfirmBox(WaitBox):
    """
    A box with two buttons: Yes and No. It can have additional handles what
    function should be called if Yes is selected. INPUT_EXIT will be close
    the box like pressing No.
    """
    def __init__(self, obj):
        WaitBox.__init__(self, obj)

        spacing = self.content_spacing
        w = int((self.get_content_size()[0] - spacing) / len(obj.buttons))
        x, y = self.get_content_pos()

        self.buttons = []
        for b in obj.buttons:
            button = Button(b.name, (x,y), w, self.button_normal)
            button.info = b
            if b.selected:
                button.set_style(self.button_selected)
            self.buttons.append(button)
            x += w + spacing
            
        y = self.add_row(self.buttons[0].get_size()[1])
        for b in self.buttons:
            b.set_pos((b.get_pos()[0], y))
            self.add_child(b)


    def update(self):
        for b in self.buttons:
            if b.info.selected:
                b.set_style(self.button_selected)
            else:
                b.set_style(self.button_normal)
        WaitBox.update(self)
