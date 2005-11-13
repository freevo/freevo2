# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# messagebox.py - popup box for text messages
# -----------------------------------------------------------------------------
# $Id$
#
# A box with a label and an OK button to close it. An additional handler can
# be used to call a function when the button is pressed. INPUT_EXIT will
# act like select.
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

__all__ = [ 'MessageBox' ]

# python imports
import logging

# freevo imports
from event import *

# gui imports
from gui.widgets.button import Button

# windows imports
from waitbox import WaitBox

# get logging object
log = logging.getLogger()


class MessageBox(WaitBox):
    """
    A box with a label and an OK button to close it.
    """
    def __init__(self, text, button_text=_('OK')):
        WaitBox.__init__(self, text)
        self.button = Button(button_text, self.get_content_pos(),
                             self.get_content_size()[0],
                             self.button_selected)
        y = self.add_row(self.button.get_size()[1])
        self.button.set_pos((self.button.get_pos()[0], y))
        self.add_child(self.button)


    def eventhandler(self, event):
        """
        Eventhandler to close the box on INPUT_ENTER or INPUT_EXIT
        """
        if event in (INPUT_ENTER, INPUT_EXIT):
            self.destroy()
            if event == INPUT_ENTER:
                self.button.select()
            return True
        return False


    def connect(self, function, *args, **kwargs):
        """
        Connect to the selection of the button.
        """
        self.button.connect(function, *args, **kwargs)

