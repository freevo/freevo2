# -*- coding: iso-8859-1 -*-
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
# Revision 1.6  2004/10/03 15:54:00  dischi
# make PopupBoxes work again as they should
#
# Revision 1.5  2004/08/24 16:42:42  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.4  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.3  2004/08/01 10:37:08  dischi
# smaller changes to stuff I need
#
# Revision 1.2  2004/07/25 18:14:05  dischi
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
from label     import Label

class ConfirmBox(PopupBox):
    """
    """
    def __init__(self, text, handler=None, handler_message=None, default_choice=0):
        PopupBox.__init__(self, text)
        self.handler = handler

        c = self.content_pos

        w = int((self.get_size()[0] - c.width - self.content_layout.spacing) / 2)
        self.b0 = Button(_('OK'), (c.x1, c.y1), w, self.button_normal)
        self.b1 = Button(_('Cancel'), (c.x1 + w + self.content_layout.spacing, c.y1),
                         w, self.button_normal)

        y = self.add_row(self.b0.get_size()[1])

        self.b0.set_pos((self.b0.get_pos()[0], y))
        self.add_child(self.b0)

        self.b1.set_pos((self.b1.get_pos()[0], y))
        self.add_child(self.b1)

        self.handler_message = handler_message
        getattr(self, 'b%s' % default_choice).set_style(self.button_selected)
        self.selected = default_choice


    def eventhandler(self, event):
        if event in (INPUT_LEFT, INPUT_RIGHT):
            self.selected = (self.selected + 1) % 2
            if self.selected == 0:
                self.b0.set_style(self.button_selected)
                self.b1.set_style(self.button_normal)
            else:
                self.b0.set_style(self.button_normal)
                self.b1.set_style(self.button_selected)
            self.update()
            return

        
        elif event == INPUT_EXIT:
            self.destroy()


        elif event == INPUT_ENTER:
            if self.selected == 0:
                if self.handler and self.handler_message:
                    # remove old content
                    self.remove_child(self.label)
                    self.remove_child(self.b0)
                    self.remove_child(self.b1)

                    # add new label
                    c = self.content_pos
                    self.label = Label(self.handler_message, (c.x1, c.y1),
                                       (self.get_size()[0] - c.width,
                                        self.get_size()[1] - c.height),
                                       self.widget_normal, 'center', 'center',
                                       text_prop=self.text_prop)
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

