# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# PopupBox - A dialog box for freevo.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
#
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------


from event import *

from Window import Window
from label  import Label


class PopupBox(Window):
    """
    Trying to make a standard popup/dialog box for various usages.
    """
    def __init__(self, text, handler=None, x=None, y=None, width=None, height=None,
                 icon=None, vertical_expansion=1, text_prop=None):

        self.handler = handler
        Window.__init__(self, x, y, width, height)

        self.text_prop = text_prop or { 'align_h': 'center',
                                        'align_v': 'center',
                                        'mode'   : 'soft',
                                        'hfill'  : True }

        self.label = Label(self.x1, self.y1, self.x2, self.y2, text,
                           self.widget_normal, 'center', 'center',
                           text_prop=self.text_prop)
        self.add(self.label)

        # resize label to fill the whole box
        space = self.content_layout.spacing
        self.label.set_position(self.x1 + space, self.y1 + space,
                                self.x2 - space, self.y2 - space)
        

    def eventhandler(self, event):
        _debug_('PopupBox: event = %s' % event, 1)

        if event == INPUT_EXIT:
            self.destroy()
        else:
            return self.parent_handler(event)
