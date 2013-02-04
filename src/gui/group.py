# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Misc group widgets used in the XML files
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


__all__ = [ 'ScaledGroup', 'Freevo' ]

import kaa.candy

from stage import config

class ScaledGroup(kaa.candy.Group):
    """
    Group with XML theme scaling. This is used for an easier XML
    files. The defined screen_width and screen_height values are used
    for the group and it is scaled to fit the actual window.

    A ScaledGroup always will the whole screen and only scales the
    widgets in it to fit the screen dimensions.
    """

    candyxml_name = 'group'
    candyxml_style = 'scaled'

    def __init__(self, pos=None, size=None, widgets=[], context=None):
        if size is None or not size[0] or not size[1]:
            raise RuntimeError('ScaledGroup needs a fixed size')
        super(ScaledGroup, self).__init__(pos, size, widgets, context)
        self.scale_x = float(self.screen_width - ( 2 * config.display.overscan.x)) / int(size[0])
        self.scale_y = float(self.screen_height - ( 2 * config.display.overscan.y)) / int(size[1])


class Freevo(ScaledGroup):
    """
    Base Freevo widget
    """
    candyxml_name = 'freevo'
    candyxml_style = None

    def __init__(self, pos=None, size=None, widgets=[], context=None):
        super(ScaledGroup, self).__init__(pos, size, [], context)
        self.children = widgets


class Layer(ScaledGroup):
    """
    Scaled version of the basic kaa.candy layer
    """
    candyxml_name = 'layer'
    candyxml_style = None

    _candy_layer_status = 0     # 0 new, 1 active, 2 destroyed

    def __init__(self, pos=None, size=None, widgets=[], context=None):
        """
        Create the layer. If no size is given the actual screen size
        is used deactivating the scaling code.
        """
        if not size:
            size = self.screen_width, self.screen_height
        size = (size[0] or self.screen_width, size[1] or self.screen_height)
        super(Layer, self).__init__(pos, size, widgets, context)

    @property
    def parent(self):
        """
        The layer widget has the stage as parent
        """
        return self.stage
