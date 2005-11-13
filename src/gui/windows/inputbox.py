# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# inputbox.py - popup box for text input
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'InputBox' ]

# python imports
import math
import logging

# freevo imports
import config
from event import *

# gui imports
import gui.displays as displays
from gui.widgets.textbox import Textbox

# windows imports
from window import Window

# get logging object
log = logging.getLogger()


class InputBox(Window):
    """
    Simple input box
    """
    def __init__(self, text, handler=None, type='text', start_value=None,
                 num_boxes=16, increment=1, min_int=-1, max_int=-1):
        Window.__init__(self)

        self.type = type
        self.cursor_pos = 0
        self.start_pos = 0
        self.letter_idx = -1
        self.last_digit = 0
        self.num_boxes = num_boxes
        self.handler = handler
        self.valbox = None
        self.valboxes = []

        self.increment = increment
        self.min_int = min_int
        self.max_int = max_int

        self.handler_message = None

        self.lc_letter_map = [ ( ' ', '+', '0', ),
                               ( '.', ',', '-', '?', '!', '1', ),
                               ( 'a', 'b', 'c', '2', ),
                               ( 'd', 'e', 'f', '3', ),
                               ( 'g', 'h', 'i', '4', ),
                               ( 'j', 'k', 'l', '5', ),
                               ( 'm', 'n', 'o', '6', ),
                               ( 'p', 'q', 'r', 's', '7', ),
                               ( 't', 'u', 'v', '8', ),
                               ( 'w', 'x', 'y', 'z', '9', ) ]

        self.uc_letter_map = [ ( ' ', '+', '0', ),
                               ( '.', ',', '-', '?', '!', '1', ),
                               ( 'A', 'C', 'D', '2', ),
                               ( 'D', 'E', 'F', '3', ),
                               ( 'G', 'H', 'I', '4', ),
                               ( 'J', 'K', 'L', '5', ),
                               ( 'M', 'N', 'O', '6', ),
                               ( 'P', 'Q', 'R', 'S', '7', ),
                               ( 'T', 'U', 'V', '8', ),
                               ( 'W', 'X', 'Y', 'Z', '9', ) ]

        self.letter_map = self.lc_letter_map

        if type == 'integer':
            self.input_width = 100
            if start_value:
                self.value = int(start_value)
            else:
                self.value = 0
        else:
            self.input_width = 330
            if start_value:
                self.value = start_value
            else:
                self.value = ' '

        width, height = self.get_content_size()

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
        self.h = displays.get().height - 100 - 2 * config.GUI_OVERSCAN_Y

        # now create the label
        self.label = Textbox(text, self.get_content_pos(), (w, self.h),
                             self.widget_normal.font, 'left',
                             'top', 'soft')

        # resize the window and set a new position
        old_w, old_h = self.get_size()
        width  = old_w + max(0, self.label.get_size()[0] - width)
        height = old_h + max(0, self.label.get_size()[1] - height)

        self.set_size((width, height))
        self.move_relative((int((old_w - width) /2) ,
                            int((old_h - height) / 2)))

        self.label.set_pos((30,30))
        self.add_child(self.label)

        self.readd_value()


    def readd_value(self):
        # now create the value box
        if self.valbox:
            self.remove_child(self.valbox)

        if self.type == 'integer':
            self.valbox = Textbox(str(self.value), (30,70),
                                  (self.input_width, self.h),
                                  self.widget_normal.font, bgcolor=(19,44,89))
            self.add_child(self.valbox)

        elif self.type == 'text':

            if self.valboxes:
                for box in self.valboxes:
                    self.remove_child(box)

            for i in range(self.num_boxes):
                # Set char to the selected char, or just a spacer
                if i+self.start_pos < len(self.value):
                    char = self.value[i+self.start_pos]
                else:
                    char = ' '

                # Different background color for selected chars
                if i == self.cursor_pos:
                    my_bgcolor=(65,118,196)
                else:
                    my_bgcolor=(19,44,89)

                cell = Textbox(str(char), (30+(i*21),70), (22, self.h),
                               self.widget_normal.font, align_h='center',
                               bgcolor=my_bgcolor)

                self.valboxes.append(cell)

                self.add_child(cell)

        self.update()


    def eventhandler(self, event):
        """
        Eventhandler to edit a text
        """

        if self.type == 'integer':
            if event == INPUT_UP:
                if self.max_int == -1 or self.max_int > self.value:
                    self.value += self.increment
                    self.readd_value()
                return True

            elif event == INPUT_DOWN:
                if self.min_int == -1 or self.value > self.min_int:
                    self.value -= self.increment
                    self.readd_value()
                return True

        elif self.type == 'text':
            if event == INPUT_UP:
                self.letter_map = self.uc_letter_map
                return True

            elif event == INPUT_DOWN:
                self.letter_map = self.lc_letter_map
                return True

            if event == INPUT_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                    self.letter_idx = -1
                elif self.start_pos > 0:
                    self.start_pos -= 1

                self.readd_value()
                return True

            elif event == INPUT_RIGHT:
                if self.cursor_pos < self.num_boxes-1:
                    self.cursor_pos += 1
                else:
                    self.start_pos += 1
                self.letter_idx = -1
                self.readd_value()
                return True

            elif event in INPUT_ALL_NUMBERS:
                if self.last_digit != event.arg:
                    self.letter_idx = 0
                else:
                    self.letter_idx = ( self.letter_idx + 1 ) % \
                                      len(self.letter_map[event.arg])
                self.last_digit = event.arg
                self.value = self.value[:self.cursor_pos+self.start_pos] + \
                             self.letter_map[event.arg][self.letter_idx] + \
                             self.value[self.cursor_pos+1+self.start_pos:]
                self.readd_value()
                return True

        if event == INPUT_EXIT:
            self.destroy()
            return True

        elif event == INPUT_ENTER:
            if self.handler:
                ret = self.handler(self.value)
                if ret == None:
                    self.destroy()
                else:
                    MessageBox(ret).show()
            else:
                self.destroy()
                return True

        return False
