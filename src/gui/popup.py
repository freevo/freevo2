# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# popup.py - Popup Window
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2009 Dirk Meyer, et al.
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

# python imports
import math

# kaa.candy import
import kaa.candy

class Popup(kaa.candy.Container):

    candyxml_name = 'popup'

    def __init__(self, text, font, color, background, content=None, context=None):
        super(Popup, self).__init__(context=context)
        self.layout = 'vertical'
        if kaa.candy.is_template(background):
            background = background()
        if kaa.candy.is_template(content):
            content = content()
        self.__text = self.context.get('text', text)
        self.__font = font
        self.__color = color
        self.background = background
        self.background.passive = True
        self.spacing = 20
        self.text = None
        self.add(self.background)
        self.xalign = self.yalign = self.ALIGN_SHRINK
        self.content = content

    def _candy_prepare(self):
        """
        Create the widgets in the message popup
        """
        super(Popup, self)._candy_prepare()
        if self.text is not None:
            return
        # create text widget
        self.text = kaa.candy.Text(None, None, self.__text, self.__font, self.__color)
        self.text.yalign = self.ALIGN_SHRINK
        self.text.xalign = self.ALIGN_CENTER
        self.add(self.text)
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
        max_height = int(self.parent.height / 1.1)
        self.text.width = max(min(int(math.sqrt(text_height * text_width * 4 / 3)), max_width), min_width)
        self.text.height = max_height
        if self.content:
            self.content.xalign = self.content.ALIGN_CENTER
            self.content.width = self.text.width
            if not self.content.parent:
                self.add(self.content)
        # prepare again with the new children
        super(Popup, self)._candy_prepare()

    def _clutter_render(self):
        """
        Render the widget
        """
        super(Popup, self)._clutter_render()
        if self.x == 0:
            self.x = max((self.parent.width - self.width) / 2, 0)
        if self.y == 0:
            self.y = max((self.parent.height - self.height) / 3, 0)

    @classmethod
    def candyxml_parse(cls, element):
        """
        Parse the XML element for parameter to create the widget.
        """
        parameter = super(Popup, cls).candyxml_parse(element)
        return dict(background=parameter.get('background'), color=element.color, font=element.font, text='')
