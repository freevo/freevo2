# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Button.py - a simple button class
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'Button' ]

# kaa imports
from kaa.notifier import Signal
from kaa.mevas.image import CanvasImage

# gui imports
from rectangle import Rectangle
from text import Text


class Button(CanvasImage):
    """
    A button widget.
    """
    def __init__(self, text, pos, width, style):
        CanvasImage.__init__(self, (width, style.font.height+4))
        self.text = text
        self.set_style(style)
        self.set_pos(pos)
        self.signal = Signal()

    def set_style(self, style):
        """
        Set new gui style
        """
        self.draw_rectangle((0,0), self.get_size(), (0, 0, 0, 0), True)
        r = Rectangle((0,0), self.get_size(),
                      style.rectangle.bgcolor,
                      style.rectangle.size,
                      style.rectangle.color,
                      style.rectangle.radius)
        self.draw_image(r, (0, 0))
        width = self.get_size()[0]
        text = Text(self.text, (0,0), (width - 20, style.font.height),
                    style.font, 'center', 'center', 'hard')
        self.draw_image(text, ((width - text.get_size()[0]) / 2, 2))


    def connect(self, function, *args, **kwargs):
        """
        Connect a callback to the select function of the button.
        """
        self.signal.connect(function, *args, **kwargs)


    def select(self):
        """
        Select the button. This will call the connected callback functions.
        """
        self.signal.emit()
