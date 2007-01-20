# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# waitbox.py - A simple box when the user has to wait
# -----------------------------------------------------------------------------
# $Id$
#
# A box with only a label and the user has no options to close it. This box
# should be used when Freevo is doing some background action and the user
# has to wait.
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

__all__ = [ 'WaitBox' ]

# python imports
import math
import logging

# freevo imports
import config

# gui imports
import gui.displays as displays
from gui.widgets.textbox import Textbox

# windows imports
from window import Window

# get logging object
log = logging.getLogger()


class WaitBox(Window):
    """
    A box with only a label and the user has no options to close it. This box
    should be used when Freevo is doing some background action and the user
    has to wait.
    """
    def __init__(self, obj):
        Window.__init__(self)

        width, height = self.get_content_size()
        text = obj.text
        
        # We need at least text_height * text_width space for the text, in
        # most cases more (because of line breaks. To make the text look
        # nice, we try 4:3 aspect of the box at first and than use the max
        # height we can get. If you are wondering about the function
        # calculating w (using sqrt and such things), my math skills told
        # me to write that, it looks ok, don't mess with it :)
        text_width  = self.widget_normal.font.stringsize(text)
        text_height = int(self.widget_normal.font.height * 1.2)
        w = max(min(int(math.sqrt(text_height * text_width * 4 / 3)),
                    displays.get().width - 60 - \
                    2 * config.GUI_OVERSCAN_X), width)
        h = displays.get().height - 100 - 2 * config.GUI_OVERSCAN_Y

        # now create the label
        self.label = Textbox(text, self.get_content_pos(), (w, h),
                             self.widget_normal.font, 'center',
                             'center', 'soft')

        # resize the window and set a new position
        old_w, old_h = self.get_size()
        width  = old_w + max(0, self.label.get_size()[0] - width)
        height = old_h + max(0, self.label.get_size()[1] - height)
        
        self.set_size((width, height))
        self.move_relative((int((old_w - width) /2) ,
                            int((old_h - height) / 2)))

        # center text
        x, y = self.get_content_pos()
        x += int((self.get_content_size()[0] - self.label.get_size()[0]) / 2)
        y += int((self.get_content_size()[1] - self.label.get_size()[1]) / 2)
        self.label.set_pos((x,y))

        # add label
        self.add_child(self.label)
        

    def add_row(self, height):
        """
        Add a row to fit objects with the given height. Resize the box if
        needed and also respect spacing. Return the y position for the new
        object. This function can only be used to add _one_ row below the label
        """
        spacing = self.content_spacing
        label_height = self.label.get_size()[1]
        add_h = max(0, label_height + spacing + height - \
                    self.get_content_size()[1])
        if add_h:
            # resize and move the box
            self.set_size((self.get_size()[0], self.get_size()[1] + add_h))
            self.move_relative((0, -int(add_h / 2)))
        # move the label height pixel (minimum value is content y1)
        x, y = self.label.get_pos()
        y = max(self.get_content_pos()[1], y - int((spacing + height) / 2))
        self.label.set_pos((x, y))
        # the y position of the text is now label pos + label height + spacing
        return y + label_height + spacing
