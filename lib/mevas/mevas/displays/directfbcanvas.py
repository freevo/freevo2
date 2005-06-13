# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directfb.py - output canvas for directfb using pydirectfb
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Mevas - MeBox Canvas System
# Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
#
# First Edition: Rob Shortt <rob@infointeractive.com>
# Maintainer:    Rob Shortt <rob@infointeractive.com>
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

_pixel_format = {
    0x00118005: 'DSPF_A8',
    0x4011420c: 'DSPF_ALUT44',
    0x00418c04: 'DSPF_ARGB',
    0x00211780: 'DSPF_ARGB1555',
    0x08100609: 'DSPF_I420',
    0x4011040b: 'DSPF_LUT8',
    0x00200801: 'DSPF_RGB16',
    0x00300c02: 'DSPF_RGB24',
    0x00400c03: 'DSPF_RGB32',
    0x00100407: 'DSPF_RGB332',
    0x00000000: 'DSPF_UNKNOWN',
    0x00200808: 'DSPF_UYVY',
    0x00200806: 'DSPF_YUY2',
    0x0810060a: 'DSPF_YV12'
    }


import mevas
import mevas.rect as rect

from directfb import *
from bitmapcanvas import *

class DirectFBCanvas(BitmapCanvas):

    def __init__(self, size, layerno):
        super(DirectFBCanvas, self).__init__(size, preserve_alpha = False,
                                             blit_once = True)
        width, height = size
        self.layerno = layerno
        print 'DEBUG: size is %sx%s' % (width, height)

        self.dfb = DirectFB()
        caps = self.dfb.getCardCapabilities()
        self.layer = self.dfb.getDisplayLayer(self.layerno)
        self.layer.setCooperativeLevel(DLSCL_ADMINISTRATIVE)
        self.layer.setConfiguration(pixelformat = DSPF_RGB32, #DSPF_ARGB,
                                    buffermode = DLBM_BACKSYSTEM,
                                    width = width, height = height)
        print 'DirectFB layer config:'
        layer_config = self.layer.getConfiguration()
        for k, v in layer_config.items():
            if not k in ('width', 'height', 'pixelformat'):
                print '  %s:  %s' % (k, v)
        print '  goemetry: %dx%d' % (layer_config.get('width'),
                                     layer_config.get('height'))
        print '  pixelformat: %s' % \
              _pixel_format[layer_config.get('pixelformat')]

        self.layer.enableCursor(0)
        self.osd = self.layer.createWindow(caps=DWCAPS_ALPHACHANNEL,
					   width=width, height=height)
        self._surface = self.osd.getSurface()
        self.osd.setOpacity(0xFF)
        self._rect = []


    def _blit(self, img, r):
        pos, size = r

        self._rect = rect.optimize_for_rendering(self._rect)
        # get the raw data from the imlib2 image as buffer
        data = img._image.get_raw_data()
        # create a new surface
        # XXX: Does overlay() handle buffer objects for data?  If not, 
        # pass str(data).
        self._surface.overlay(DSPF_ARGB, data)
        self._surface.flip(DSFLIP_WAIT)
        return
