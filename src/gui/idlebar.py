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

from widget import Widget

# get logging object
log = logging.getLogger()

class Idlebar(Widget):

    candyxml_style = 'idlebar'

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

    def show(self):
        self.animate('EASE_IN_CUBIC', 0.2, opacity=255)

    def hide(self):
        self.animate('EASE_OUT_CUBIC', 0.2, opacity=0)
