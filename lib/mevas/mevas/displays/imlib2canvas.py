# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# imlib2canvas.py - output display for imlib2 window
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Mevas - MeBox Canvas System
# Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
#
# First Edition: Jason Tackaberry <tack@sault.org>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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


import time
import mevas
import Imlib2

from bitmapcanvas import *

class Imlib2Canvas(BitmapCanvas):

    def __init__(self, size, dither = True, blend = False):
        super(Imlib2Canvas, self).__init__(size, preserve_alpha = blend)
        self._display = Imlib2.Display(size, dither, blend)

    def _blit(self, img, r):
        pos, size = r
        if isinstance(img, mevas.imagelib.get_backend("imlib2").Image):
            self._display.render(img._image, pos, pos, size)
        else:
            if img.size != size:
                img = imagelib.crop(img, pos, size)

            data = img.get_raw_data("RGB")
            img = Imlib2.new( size, data, "RGB" )
            self._display.render(img, pos)
