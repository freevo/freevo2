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

class ConfirmBox(PopupBox):
    """
    """
    def __init__(self, text, handler=None, handler_message=None, default_choice=0,
                 x=None, y=None, width=None, height=None, icon=None, vertical_expansion=1,
                 text_prop=None):
        PopupBox.__init__(self, 'ConfirmBox is broken', handler, x, y, width, height,
                          icon, vertical_expansion, text_prop)
        return
#         self.b0 = Button(self.x1, self.y1, self.x2, self.y2, _('OK'),
#                          self.button_normal)
#         self.add(self.b0)

#         self.b1 = Button(self.x1, self.y1, self.x2, self.y2, _('Cancel'),
#                          self.button_normal)
#         self.add(self.b1)

#         # FIXME: that can't be correct
#         space = self.content_layout.spacing * 2

#         # get height of the button and set it to set bottom
#         ydiff = self.b0.y2 - (self.y2 - space)

#         # both buttons should have the same width
#         bwidth = (self.x2 - self.x1 - 3 * space) / 2
#         b1x    = self.x1 + space
#         b2x    = self.x1 + 2 * space + bwidth

#         self.b0.set_position(b1x, self.b0.y1 - ydiff,
#                              b1x + bwidth, self.b0.y2 - ydiff)

#         self.b1.set_position(b2x, self.b1.y1 - ydiff,
#                              b2x + bwidth, self.b1.y2 - ydiff)

#         # resize label to fill the rest of the box
#         self.label.set_position(self.x1 + space, self.y1 + space, self.x2 - space,
#                                 self.y2 - space + ydiff - space)
        
#         self.handler_message = handler_message
#         getattr(self, 'b%s' % default_choice).set_style(self.button_selected)
#         self.selected = default_choice


#     def eventhandler(self, event):
#         if event in (INPUT_LEFT, INPUT_RIGHT):
#             self.selected = (self.selected + 1) % 2
#             if self.selected == 0:
#                 self.b0.set_style(self.button_selected)
#                 self.b1.set_style(self.button_normal)
#             else:
#                 self.b0.set_style(self.button_normal)
#                 self.b1.set_style(self.button_selected)
#             self.screen.update()
#             return

        
#         elif event == INPUT_EXIT:
#             self.destroy()


#         elif event == INPUT_ENTER:
#             if self.selected == 0:
#                 if self.handler and self.handler_message:
#                     # resize the label to fit the whole box
#                     space = self.content_layout.spacing
#                     self.label.set_position(self.x1 + space, self.y1 + space,
#                                             self.x2 - space, self.y2 - space)
#                     # set new next
#                     self.label.set_text(self.handler_message)
#                     # remove buttons
#                     self.remove(self.b0)
#                     self.remove(self.b1)
#                     self.screen.update()
#                 else:
#                     self.destroy()

#                 if self.handler:
#                     self.handler()
#                     if self.handler_message:
#                         self.destroy()
#             else:
#                 self.destroy()

#         else:
#             return self.parent_handler(event)
