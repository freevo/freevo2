# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# popups.py - popup boxes for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines some simple popup boxes used in Freevo. The boxes are
#
# WaitBox:
# A box with only a label and the user has no options to close it. This box
# should be used when Freevo is doing some background action and the user
# has to wait.
#
# MessageBox:
# A box with a label and an OK button to close it. An additional handler can
# be used to call a function when the button is pressed. INPUT_EXIT will
# act like select.
#
# ConfirmBox:
# A box with two buttons: Yes and No. It can have additional handles what
# function should be called if Yes is selected. INPUT_EXIT will be close
# the box like pressing No.
#
# ProgressBox:
# A box showing a progress bar. There is no wait for the user to close the
# box, this has to be done from the outside.
#
#
# TODO: o make InputBox waork again
#       o rename PopupBox->WaitBox and AlertBox->MessageBox
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

__all__ = [ 'WaitBox', 'MessageBox', 'ConfirmBox', 'ProgressBox', 'InputBox',
            'PopupBox', 'AlertBox' ]

# python imports
import math
import notifier

# freevo imports
import config
from event import *

# gui imports
import displays
from window import Window
from widgets.textbox  import Textbox
from widgets.button import Button
from widgets.progressbar import Progressbar


class WaitBox(Window):
    """
    A box with only a label and the user has no options to close it. This box
    should be used when Freevo is doing some background action and the user
    has to wait.
    """
    def __init__(self, text):
        Window.__init__(self)

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
                    displays.get_display().width - 60 - \
                    2 * config.OSD_OVERSCAN_X), width)
        h = displays.get_display().height - 100 - 2 * config.OSD_OVERSCAN_Y

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

    
    def eventhandler(self, event):
        """
        Eventhandler for the box. A WaitBox can handle no events, something
        from the outside must close the box.
        """
        return False
    



class MessageBox(WaitBox):
    """
    A box with a label and an OK button to close it. An additional handler can
    be used to call a function when the button is pressed. INPUT_EXIT will
    act like select.
    """
    def __init__(self, text, handler=None, button_text=_('OK')):
        WaitBox.__init__(self, text)
        self.handler = handler
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
            if self.handler:
                self.handler()
            return True
        return False



class ConfirmBox(WaitBox):
    """
    A box with two buttons: Yes and No. It can have additional handles what
    function should be called if Yes is selected. INPUT_EXIT will be close
    the box like pressing No.
    """
    def __init__(self, text, handler=None, handler_message=None,
                 default_choice=0):
        WaitBox.__init__(self, text)
        self.handler = handler

        spacing = self.content_spacing
        w = int((self.get_content_size()[0] - spacing) / 2)
        x, y = self.get_content_pos()
        self.b0 = Button(_('Yes'), (x,y), w, self.button_normal)
        x += w + spacing
        self.b1 = Button(_('No'), (x, y), w, self.button_normal)

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



class ProgressBox(WaitBox):
    """
    A box showing a progress bar. There is no wait for the user to close the
    box, this has to be done from the outside.
    """
    def __init__(self, text, full=0):
        WaitBox.__init__(self, text)

        h = 25
        y = self.add_row(h)
        x = self.get_content_pos()[0]
        style = self.widget_normal.rectangle
        self.bar = Progressbar((x, y), (self.get_content_size()[0], h),
                               2, style.color, style.bgcolor, 0, None,
                               self.widget_selected.rectangle.bgcolor, 0, full)
        self.add_child(self.bar)


    def tick(self):
        """
        increase the bar position
        """
        notifier.step( False, False )
        self.bar.tick()
        self.update()



# broken box

class InputBox(MessageBox):
    """
    """
    def __init__(self, text, handler=None, type='text', input_text='',
                 numboxes=0):
        MessageBox.__init__(self, 'input box not working', handler)
        


# compability classes

class PopupBox(WaitBox):
    pass

class AlertBox(MessageBox):
    pass
