# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# logo.py - IdleBarPlugin for showing a freevo logo
# -----------------------------------------------------------------------
# $Id:
#
# -----------------------------------------------------------------------
# $Log:
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------- */

import os

import gui
import config
from plugins.idlebar import IdleBarPlugin

class PluginInterface(IdleBarPlugin):
    """
    Display the freevo logo in the idlebar
    """
    def __init__(self, image=None):
        IdleBarPlugin.__init__(self)
        self.image  = image
        self.file   = file
        self.object = None


    def draw(self, width, height):
        if not self.image:
            image = gui.get_image('logo')
        else:
            image = os.path.join(config.IMAGE_DIR, self.image)

        if self.objects and self.file == image:
            return self.NO_CHANGE

        self.file = image
        self.clear()

        i = gui.imagelib.load(image, (None, height + 10))
        if not i:
            return 0

        self.objects.append(gui.Image(i, (0, 0)))

        return i.width
