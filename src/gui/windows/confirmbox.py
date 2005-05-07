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
    def __init__(self, text, handler=None, handler_message=None,
                 button0_text = _('Yes'), button1_text = _('No'),
                 default_choice=0):
        WaitBox.__init__(self, text)
        self.handler = handler

        spacing = self.content_spacing
        w = int((self.get_content_size()[0] - spacing) / 2)
        x, y = self.get_content_pos()
        self.b0 = Button(button0_text, (x,y), w, self.button_normal)
        x += w + spacing
        self.b1 = Button(button1_text, (x, y), w, self.button_normal)

        y = self.add_row(self.b0.get_size()[1])

        self.b0.set_pos((self.b0.get_pos()[0], y))
        self.add_child(self.b0)

        self.b1.set_pos((self.b1.get_pos()[0], y))
        self.add_child(self.b1)

        self.handler_message = handler_message
        getattr(self, 'b%s' % default_choice).set_style(self.button_selected)
        self.selected = default_choice


    def eventhandler(self, event):
        """
        Eventhandler to toggle the selection or press the button
        """
        if event in (INPUT_LEFT, INPUT_RIGHT):
            self.selected = (self.selected + 1) % 2
            if self.selected == 0:
                self.b0.set_style(self.button_selected)
                self.b1.set_style(self.button_normal)
            else:
                self.b0.set_style(self.button_normal)
                self.b1.set_style(self.button_selected)
            self.update()
            return True


        elif event == INPUT_EXIT:
            self.destroy()
            return True

        elif event == INPUT_ENTER:
            if self.selected == 0:
                if self.handler and self.handler_message:
                    # remove old content
                    self.remove_child(self.label)
                    self.remove_child(self.b0)
                    self.remove_child(self.b1)

                    # add new label
                    self.label = Textbox(self.handler_message,
                                         self.get_content_pos(),
                                         self.get_content_size(),
                                         self.widget_normal.font,
                                         'center', 'center', 'soft')
                    self.add_child(self.label)
                    self.update()
                else:
                    self.destroy()

                if self.handler:
                    self.handler()
                    if self.handler_message:
                        self.destroy()
            else:
                self.destroy()
            return True
        return False
