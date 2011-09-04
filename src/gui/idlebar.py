# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# idlebar.py
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2008-2011 Dirk Meyer, et al.
#
# First edition: Dirk Meyer <dischi@freevo.org>
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

import logging

import kaa.candy

# get logging object
log = logging.getLogger()

class Idlebar(kaa.candy.Group):
    candyxml_name = 'idlebar'

    # properties
    __visible = False

    def __init__(self, *args, **kwargs):
        super(Idlebar, self).__init__(*args, **kwargs)
        self.plugins = self.get_widget('plugins')

    def connect(self, plugin):
        """
        Connect an idlebar plugin
        """
        plugin.connect(self.plugins)

    def sync_layout(self, size):
        """
        Sync layout changes and calculate intrinsic size based on the
        parent's size.
        """
        super(Idlebar, self).sync_layout(size)
        x0, x1 = 0, self.plugins.width
        for widget in self.plugins.children:
            step = widget.intrinsic_size[0] + 20 # FIXME: using padding variable from theme
            if widget.xalign == widget.ALIGN_RIGHT:
                widget.x = x1 - widget.width
                x1 -= step
            else:
                widget.x = x0
                x0 += step

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, visible):
        if self.__visible == visible:
            return
        self.__visible = visible
        if visible:
            self.animate('EASE_IN_CUBIC', 0.2, opacity=255)
        else:
            self.animate('EASE_OUT_CUBIC', 0.2, opacity=0)
