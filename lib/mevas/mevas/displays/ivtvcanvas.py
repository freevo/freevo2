# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# ivtvcanvas.py - output display on ivtv osd
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

import time, os, fcntl, struct, math
import mevas

from bitmapcanvas import *
from mevas import imagelib

IVTVFB_IOCTL_SET_STATE = 1074282498
IVTVFB_IOCTL_PREP_FRAME = 1074544643
FBIOGET_FSCREENINFO = 17922

class IvtvCanvas(BitmapCanvas):

    def __init__(self, size, fb_device = "/dev/fb0"):
        super(IvtvCanvas, self).__init__(size, preserve_alpha = True,
					 slices = True)
        self._fb_device = fb_device

        self._fd = os.open(fb_device, os.O_RDWR)
        r = fcntl.ioctl(self._fd, FBIOGET_FSCREENINFO, " " * 68)
        r = struct.unpack("16sLLLLLHHHLLLLHHHH", r)
        self._fb_size, self._fb_stride = r[2], r[9]

        self._fb_height = self._fb_size / self._fb_stride
        self._fb_width = self._fb_stride / 4
        self._set_ivtv_alpha(255)


    def __del__(self):
        self.clear()
        # We can't call update() because self.canvas weakref is dead.
        self.child_paint(self)


    def _set_ivtv_alpha(self, alpha):
        r = struct.pack("LL", 13L, alpha)
        r = fcntl.ioctl(self._fd, IVTVFB_IOCTL_SET_STATE, r)


    def _blit(self, img, region):
        scale_x = self._fb_width / float(img.width)
        scale_y = self._fb_height / float(img.height)

        # FIXME: This is weird, but when we blit an image whose height is
        # less than 60 or so, things go all screwy.
        offset_h = 5
        if region[1][1] < 50/scale_y:
            offset_h = int(50/scale_y)
        region = rect.offset(region, (0, -offset_h), (0, offset_h*2) )
        region = rect.clip(region, ((0, 0), self.get_size()) )

        # Translate the canvas region to the framebuffer region.
        dst_region = rect.translate(region, scale = (scale_x, scale_y),
				    scale_pos = True)
        # Scale the slice to the necessary aspect.
        img = imagelib.scale(img, (self._fb_width, dst_region[1][1]),
               (0, region[0][1]), (img.width, region[1][1]) )

        data = img.get_raw_data("BGRA")
        address = data.get_buffer_address()
        assert( address != 0)
        start = dst_region[0][1] * self._fb_stride
        size = dst_region[1][1] * self._fb_stride
        #args = struct.pack("PLi", address, 0, len(data))
        args = struct.pack("PLi", address, start, size)
        r = fcntl.ioctl(self._fd, IVTVFB_IOCTL_PREP_FRAME, args)
