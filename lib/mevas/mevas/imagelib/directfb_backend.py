# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directfb_backend.py - DirectFB backend for mevas imagelib.
#
# Note: This doesn't work yet don't don't bother trying. :)
#
# TODO: 
#      -fontpath support
#      -SurfaceDescription support in pydirectfb
#      -image transformations
#      -revive blend method
#      -support other raw formats
#      -revise _capabilities
#      -a way to save an image to disk
#      -a bunch of other stuff I forgot
#
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Mevas - MeBox Canvas System
# Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
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
import copy
import types
import traceback

# mevas imports
import base

# pydirectfb
from directfb import *
import directfb.Font as DFBFont


_capabilities =  {
    "to-raw-formats": ["BGRA", ],
    "from-raw-formats": ["BGRA", ],
    "preferred-format": "BGRA",
    "shmem": False,
    "pickling": True,
    "unicode": True,
    "layer-alpha": True,
    "alpha-mask": True,
    "cache": True
    }


_dfb_pixel_format = {
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

_mevas_pixel_format = {
    DSPF_A8       : '',
    DSPF_ALUT44   : '',
    DSPF_ARGB     : 'BGRA',
    DSPF_ARGB1555 : '',
    DSPF_I420     : '',
    DSPF_LUT8     : '',
    DSPF_RGB16    : '',
    DSPF_RGB24    : '',
    DSPF_RGB32    : '',
    DSPF_RGB332   : '',
    DSPF_UNKNOWN  : 'DSPF_UNKNOWN',
    DSPF_UYVY     : '',
    DSPF_YUY2     : '',
    DSPF_YV12     : ''
    }



class Image(base.Image):
    """
    A DirectFB based image class.
    Some methods here are left unimplimented until we find a way to easily
    do what's needed.  It may be possible to still use pyimlib2 for some of
    the things DirectFB doesn't support.
    """
    def __init__(self, image_or_filename):
        self.imageDescription = None
        self.filename = None

        if isinstance(image_or_filename, Image):
            self._image = image_or_filename._image
        elif isinstance(image_or_filename, Surface):
            self._image = image_or_filename
        elif isinstance(image_or_filename, ImageProvider):
            self._image = createSurface(desc=image_or_filename.getSurfaceDescription))
        elif type(image_or_filename) in types.StringTypes:
            # Should we copy(provider.getSurfaceDescription()) 
            # then del(provider)?
            self.filename = image_or_filename
            provider = createImageProvider(self.filename)
            self.imageDescription = provider.getImagedescription()
            self._image = createSurface(desc=provider.getSurfaceDescription))
        elif isinstance(image_or_filename, SurfaceDescription):
            self._image = createSurface(desc=image_or_filename)
        else:
            raise ValueError, "Unsupported image type: %s" % \
                  type(image_or_filename)

    def __getattr__(self, attr):
        if attr == "format":
            return _mevas_pixel_format[self._image.getSurfaceDescription().format]

        elif attr in ("width", "height", "size", "pitch"):
            return getattr(self._image.getSurfaceDescription(), attr)

        if attr in ("mode", "filename", "has_alpha", "rowstride", "get_pixel"):
            return getattr(self._image, attr)

        return super(Image, self).__getattr__(attr)


    def get_raw_data(self, format = "BGRA"):
        if format == self.format:
            return str(self._image.getSurfaceDescription().data)

        else:
            # Must decide how to deal with other formats.
            # Maybe we can blit onto a new surface with the desired format
            # then return its surfaceDescription.data.
            return None


    # TODO: Maybe we can add a tools section to pydirectfb to help
    #       with some image transformations, or use pyimlib2.

    def rotate(self, angle):
        pass


    def flip(self):
        pass


    def mirror(self):
        pass


    def scale(self, size, src_pos = (0, 0), src_size = (-1, -1)):
        # TODO: use StretchBlit
        # self._image =  self._image.scale(size, src_pos, src_size)
        pass


    def blend(self, srcimg, dst_pos = (0, 0), dst_size = (-1, -1),
          src_pos = (0, 0), src_size = (-1, -1),
          alpha = 255, merge_alpha = True):
        #return self._image.blend(srcimg._image, src_pos, src_size, dst_pos,
        #                         dst_size, alpha, merge_alpha)
        pass


    def clear(self, pos = (0, 0), size = (-1, -1)):
        pass


    def draw_mask(self, maskimg, pos):
        pass


    def copy(self):
        return Image(copy(self._image))


    def set_font(self, font_or_fontname):
        if isinstance(font_or_fontname, Font):
            font_or_fontname = font_or_fontname._font
        return self._image.setFont(font_or_fontname._font)


    def get_font(self):
        return Font(self._image.getFont())


    def set_color(self, color):
        try:
            self._image.setColor(color)
        except:
            traceback.print_exc()


    def draw_text(self, pos, text, color = None, font_or_fontname = None):

        if font_or_fontname:
            if isinstance(font_or_fontname, Font):
                font_or_fontname = font_or_fontname._font

            if self._image.getFont() != font_or_fontname:
                self.set_font(font_or_fontname)

        if color:
            self.set_color(color)

        return self._image.drawString(text, pos[0], pos[1], DSTF_LEFT | DSTF_TOP)


    def draw_rectangle(self, pos, size, color, fill = True):
        self.set_color(color)
       
        self._image.drawRectangle(pos[0], pos[1], size[0], size[1])

        if fill:
            self._image.fillRectangle(pos[0], pos[1], size[0], size[1])


    def draw_ellipse(self, center, size, amplitude, fill = True):
        # TODO: find some way to easily draw an ellipse as there's
        #       no way to in the DirectFB API.  Maybe find (or build)
        #       another library.
        pass


    def move_to_shmem(self, format = "BGRA", id = None):
        # TODO: decide if we need this, if not, remove it
        pass


    def save(self, filename, format = None):
        # TODO: find a way to save an image to file because
        #       IDirectFBImageProvider doesn't support this.
        pass


    def get_capabilities(self):
        return _capabilities


    def crop(self, pos, size):
        #self._image = self._image.crop(pos, size)
        pass


    def scale_preserve_aspect(self, size):
        self.scale(size)


    def copy_rect(self, src_pos, size, dst_pos):
        self._image.blit(self._image, dst_pos[0], dst_pos[1], 
                         (src_pos[0], src_pos[1], size[0], size[1]))




class Font(base.Font):
    def __init__(self, fontdesc, color = (255, 255, 255, 255)):
        (name, size) = fontdesc.split('/')
        fontfile = '/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf'
        # TODO: fontfile = find.in.fontpath(name)
        self._font = DFBFont(fontfile, height=size)


    def get_text_size(self, text):
        return self._font.getStringWidth(text)


    def set_color(self, color):
        pass


    def __getattr__(self, attr):
        if attr in ("ascent", "descent", "max_ascent", "max_descent"):
            return getattr(self._font, attr)
        return super(Font, self).__getattr__(attr)



def get_capabilities():
    return _capabilities


def open(file):
    return Image(file)


def new(size, rawdata = None, from_format = "BGRA"):
    if from_format not in _capabilities["from-raw-formats"]:
        raise ValueError, "Unsupported raw format: %s" % from_format
    # TODO: create a new SurfaceDescription using rawdata then pass it
    #       through Image contructor.
    pass



def add_font_path(path):
    pass


def load_font(font, size):
    pass



def scale(image, size, src_pos = (0, 0), src_size = (-1, -1)):
    image = copy.copy(image)
    image.scale(size, src_pos, src_size)
    return image


def crop(image, pos, size):
    image = copy.copy(image)
    image.crop(pos, size)
    return image


def rotate(image, angle):
    image = image.copy()
    image.rotate(angle)
    return image


def scale_preserve_aspect(image, size):
    image = copy.copy(image)
    image.scale_preserve_aspect(size)
    return image


def thumbnail(src, dst, size):
    # TODO: return a new Image from surface size, then stretchblit src onto it
    pass

