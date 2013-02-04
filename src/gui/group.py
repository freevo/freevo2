# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# group.py - misc group widgets
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2012-2013 Dirk Meyer, et al.
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

__all__ = [ 'ScaledGroup', 'Freevo' ]

import kaa.candy

from stage import config

class ScaledGroup(kaa.candy.Group):
    """
    Group with XML theme scaling
    """
    candyxml_name = 'group'
    candyxml_style = 'scaled'

    __screen_width = None
    __screen_height = None

    @property
    def screen_width(self):
        return self.__screen_width

    @screen_width.setter
    def screen_width(self, value):
        self.__screen_width = int(value)
        self.scale_x = float(self.ssize[0] - ( 2 * config.display.overscan.x)) / int(value)

    @property
    def screen_height(self):
        return self.__screen_height

    @screen_height.setter
    def screen_height(self, value):
        self.__screen_height = int(value)
        self.scale_y = float(self.ssize[1] - ( 2 * config.display.overscan.y)) / int(value)


class Freevo(ScaledGroup):
    """
    Base Freevo widget
    """
    candyxml_name = 'freevo'
    candyxml_style = None

    def __init__(self, pos=None, size=None, widgets=[], context=None):
        super(ScaledGroup, self).__init__(pos, size, [], context)
        self.children = widgets


# class Content(ScaledGroup):
#     """
#     Base Freevo widget
#     """
#     candyxml_name = 'content'
#     candyxml_style = None


class Layer(ScaledGroup):

    candyxml_name = 'layer'
    candyxml_style = None

    _candy_layer_status = 0     # 0 new, 1 active, 2 destroyed

    def __init__(self, pos=None, size=None, ssize=None, widgets=[], context=None):
        if not size:
            size = ssize
        size = (size[0] or ssize[0], size[1] or ssize[1])
        self.screen_width, self.screen_height = size
        super(Layer, self).__init__(pos, size, widgets, context)

    @property
    def parent(self):
        return self.stage
