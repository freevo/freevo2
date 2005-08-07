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
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
    def __init__(self, text, buttons=(_('Yes'), _('No')), default_choice=0):
        WaitBox.__init__(self, text)

        spacing = self.content_spacing
        w = int((self.get_content_size()[0] - spacing) / len(buttons))
        x, y = self.get_content_pos()

        self.buttons = []
        for btext in buttons:
            self.buttons.append(Button(btext, (x,y), w, self.button_normal))
            x += w + spacing
            
        y = self.add_row(self.buttons[0].get_size()[1])
        for b in self.buttons:
            b.set_pos((b.get_pos()[0], y))
            self.add_child(b)

        self.selected = self.buttons[default_choice]
        self.selected.set_style(self.button_selected)
        

    def connect(self, button, function, *args, **kwargs):
        """
        Connect a callback to a button by it's number. If nothing is sepcified
        in the constructor, 0 is yes and 1 is no.
        """
        self.buttons[button].connect(function, *args, **kwargs)
        

    def eventhandler(self, event):
        """
        Eventhandler to toggle the selection or press the button
        """
        if event in (INPUT_LEFT, INPUT_RIGHT):
            # Toggle selection
            self.selected.set_style(self.button_normal)
            index = self.buttons.index(self.selected)
            if event == INPUT_LEFT:
                index = (index + 1) % len(self.buttons)
            elif index == 0:
                index = len(self.buttons) - 1
            else:
                index = index - 1
            self.selected = self.buttons[index]
            self.selected.set_style(self.button_selected)
            self.update()
            return True

        elif event == INPUT_EXIT:
            self.destroy()
            return True

        elif event == INPUT_ENTER:
            self.selected.select()
            self.destroy()
            return True
        
        return False
