# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# PopupBox - A dialog box for freevo.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
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
    def __init__(self, text):

        Window.__init__(self)
        c = self.content_pos

        width  = self.width - c.width
        height = self.height - c.height

        self.text_prop = { 'align_h': 'center',
                           'align_v': 'center',
                           'mode'   : 'soft',
                           'hfill'  : True }

        self.label = Label(text, (c.x1, c.y1), (width, height),
                           self.widget_normal, 'center', 'center',
                           text_prop=self.text_prop, scale=True)

        old_w, old_h = self.get_size()
        width  = max(old_w, self.label.get_size()[0] + c.width)
        height = max(old_h, self.label.get_size()[1] + c.height)

        self.set_size((width, height))
        self.move_relative((int((old_w - width) /2) , int((old_h - height) / 2)))

        # center text
        x = int((width - c.width - self.label.get_size()[0]) / 2) + c.x1
        y = int((height - c.height - self.label.get_size()[1]) / 2) + c.y1

        self.label.set_pos((x,y))
        self.add_child(self.label)
        

    def add_row(self, height):
        """
        Add a row to fit objects with the given height. Resize the box if needed
        and also respect spacing. Return the y position for the new object. This
        function can only be used to add _one_ row below the label
        """
        spacing = self.content_layout.spacing
        label_height = self.label.get_size()[1]
        box_height = self.get_size()[1]
        add_to_height = max(0, label_height + spacing + height + \
                            self.content_pos.width - box_height)
        if add_to_height:
            # resize and move the box
            self.set_size((self.get_size()[0], box_height + add_to_height))
            self.move_relative((0, -int(add_to_height/2)))

        # move the label height pixel (minimum value is content y1)
        x, y = self.label.get_pos()
        y = max(self.content_pos.y1, y - spacing - height)
        self.label.set_pos((x, y))
        # the y position of the text is now label pos + label height + spacing
        return y + label_height + spacing

    
    def eventhandler(self, event):
        _debug_('PopupBox: event = %s' % event, 1)

        if event == INPUT_EXIT:
            self.destroy()
