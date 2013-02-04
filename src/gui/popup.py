# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# popup.py - Popup Window
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2009-2013 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

__all__ = [ 'Popup', 'Button' ]

# python imports
import copy
import math

# kaa.candy import
import kaa.candy

from widget import Widget

kaa.candy.Eventhandler.signatures['button-select'] = 'prev,next,secs'

class Popup(Widget):

    candyxml_style = 'popup'
    context_sensitive = True

    selected = None

    def __init__(self, text, font, color, background, button_template, layer=None, context=None):
        super(Popup, self).__init__(layer=layer, context=context)
        if kaa.candy.is_template(background):
            background = background()
        self.background = background
        self.background.passive = True
        self.background.parent = self
        self.__text = self.context.get('text', text)
        self.__font = font
        self.text = kaa.candy.Text(None, None, self.__text, self.__font, color)
        self.text.parent = self
        self.buttons = kaa.candy.Group()
        self.buttons.parent = self
        for button in context.get('buttons', []):
            button = button_template(obj=button, context=self.context)
            button.parent = self.buttons

    def sync_layout(self, size):
        super(Popup, self).sync_layout(size)
        padding_x = padding_y = 20 # FIXME: padding from theme
        # We need at least text_height * text_width space for the text, in
        # most cases more (because of line breaks. To make the text look
        # nice, we try 4:3 aspect of the box at first and than use the max
        # height we can get. If you are wondering about the function
        # calculating w (using sqrt and such things), my math skills told
        # me to write that, it looks ok, don't mess with it :)
        text_width  = self.__font.get_width(self.__text)
        text_height = int(self.__font.get_height(2) * 1.2)
        min_width = self.parent.width / 3
        max_width = int(self.parent.width / 1.1)
        text_width = max(min(int(math.sqrt(text_height * text_width * 4 / 3)), max_width), min_width)
        # check buttons
        button_width = button_height = 0
        for button in self.buttons.children:
            button_width = max(button_width, button.label.intrinsic_size[0])
            button_height = max(button_height, button.label.intrinsic_size[1])
        width = max((button_width + padding_x) * len(self.buttons.children), text_width)
        # layout children
        self.text.x = padding_x
        self.text.y = padding_y
        self.text.width = width
        self.text.height = int(self.parent.height / 1.1)
        self.buttons.x = padding_x
        self.buttons.y = self.text.intrinsic_size[1] + 2 * padding_y
        self.buttons.width = width
        self.width = width + 2 * padding_x
        self.height = self.buttons.y + button_height + padding_y
        # layout buttons
        if self.buttons.children:
            button_width = (width / len(self.buttons.children)) - padding_x
            button_x = 0
            for button in self.buttons.children:
                button.x = button_x
                button_x += button_width + padding_x
                button.width = button_width
                button.height = button_height
        self.x = max((self.parent.width - self.width) / 2, 0)
        self.y = max((self.parent.height - self.height) / 3, 0)
        # and re-layout again
        super(Popup, self).sync_layout(size)
        # select button
        if not self.selected:
            self.select()

    def select(self):
        for button in self.buttons.children:
            if button.obj.selected and button != self.selected:
                button.emit('button-select', self.selected, button, 0.2)
                self.selected = button

    def sync_context(self):
        super(Popup, self).sync_context()
        self.select()

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        parameter = super(Popup, cls).candyxml_parse(element)
        return kaa.candy.XMLdict(background=parameter.get('background'), color=element.color,
            font=element.font, text='', button_template=parameter.get('button'),
            layer=element.layer)

class Button(kaa.candy.AbstractGroup):

    candyxml_name = 'button'

    def __init__(self, pos=None, size=None, obj=None, font='Vera:24', color='0xffffff',
                 background=None, context=None):
        super(Button, self).__init__(pos, size, context)
        if background:
            if kaa.candy.is_template(background):
                background = background()
            background.passive = True
            self.add(background)
            self.background = background
        self.label = kaa.candy.Label(None, size, color, font, obj.name)
        self.label.xalign = self.label.ALIGN_CENTER
        self.add(self.label)
        self.obj = obj

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        return super(Button, cls).candyxml_parse(element).update(font=element.font, color=element.color)
