# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directfb_backend.py - DirectFB backend for mevas imagelib.
#
# Note: This doesn't work yet don't don't bother trying. :)
#
# TODO: 
#      -improve SurfaceDescription support in pydirectfb (set data)
#      -image transformations
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
import glob
import os.path

# mevas imports
import base

# pydirectfb
from directfb import *

dfb = DirectFB()


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

_font_path = []
_fonts = {}



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
        self.has_alpha = 1
        self._color = (255, 255, 255, 255)

        if isinstance(image_or_filename, Image):
            self._image = image_or_filename._image
        elif isinstance(image_or_filename, Surface):
            self._image = image_or_filename
        elif isinstance(image_or_filename, ImageProvider):
            self._image = dfb.createSurface(description=image_or_filename.getSurfaceDescription())
            image_or_filename.renderTo(self._image)
        elif type(image_or_filename) in types.StringTypes:
            self.filename = image_or_filename
            provider = dfb.createImageProvider(self.filename)
            self.imageDescription = provider.getImageDescription()
            self._image = dfb.createSurface(description=provider.getSurfaceDescription())
            provider.renderTo(self._image)
        elif isinstance(image_or_filename, SurfaceDescription):
            self._image = dfb.createSurface(description=image_or_filename)
        else:
            raise ValueError, "Unsupported image type: %s" % \
                  type(image_or_filename)

        self._image.setBlittingFlags(DSBLIT_BLEND_ALPHACHANNEL)
        self._image.setDrawingFlags(DSDRAW_BLEND)


    def __getattr__(self, attr):
        if attr == "format":
            return _mevas_pixel_format[self._image.getPixelFormat()]

        elif attr == "width":
            return self._image.getSize()[0]

        elif attr == "height":
            return self._image.getSize()[1]

        elif attr == "size":
            return self._image.getSize()

        print 'DEBUG: want attr "%s"' % attr

        if attr in ("pitch"):
            return getattr(self._image.getSurfaceDescription(), attr)

        elif attr in ("mode", "has_alpha", "rowstride", "get_pixel"):
            return getattr(self._image, attr)

        return base.Image.__getattr__(self, attr)


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
        print 'Image.rotate not implimented'


    def flip(self):
        print 'Image.flip not implimented'


    def mirror(self):
        print 'Image.mirror not implimented'


    def scale(self, size, src_pos = (0, 0), src_size = (-1, -1)):
        print 'Image.scale called'
         
        if src_size[0] == -1:
            s_w = self.width
        else:
            s_w = src_size[0]

        if src_size[1] == -1:
            s_h = self.height
        else:
            s_h = src_size[1]

        newsurf = dfb.createSurface(caps=self._image.getCapabilities(),
                                    width=size[0], height=size[1],
                                    pixelformat=self._image.getPixelFormat())

        newsurf.stretchBlit(self._image,
                            (src_pos[0], src_pos[1], s_w, s_h),
                            (0, 0, size[0], size[1]))

        self._image = newsurf


    def blend(self, srcimg, dst_pos = (0, 0), dst_size = (-1, -1),
              src_pos = (0, 0), src_size = (-1, -1),
              alpha = 255, merge_alpha = True):

        print 'Image.blend called'
        # print 'src_size: %s,%s' % src_size
        # print 'src_pos: %s,%s' % src_pos
        # print 'dst_pos: %s,%s' % dst_pos

        blittingFlags = DSBLIT_NOFX  

        if alpha == 256: 
            merge_alpha = False
        elif merge_alpha:
            blittingFlags |= DSBLIT_BLEND_ALPHACHANNEL 

        self._image.setBlittingFlags(blittingFlags)

        real_src_size = srcimg._image.getSize()

        if src_size[0] == -1:
            s_w = real_src_size[0]
        else:
            s_w = src_size[0]

        if src_size[1] == -1:
            s_h = real_src_size[1]
        else:
            s_h = src_size[1]

        if dst_size[0] == -1:
            d_w = real_src_size[0]
        else:
            d_w = dst_size[0]

        if dst_size[1] == -1:
            d_h = real_src_size[1]
        else:
            d_h = dst_size[1]

        if (s_w, s_h) == (d_w, d_h):
            # no scaling involved
            print 'use blit: %s %s (%s %s %s %s)' % (dst_pos[0], dst_pos[1],src_pos[0], src_pos[1], s_w, s_h)
            #
            # XXX: This blit call segfaults!!!
            #
            #self._image.blit(srcimg._image, dst_pos[0], dst_pos[1], 
            #                 (src_pos[0], src_pos[1], s_w, s_h))
            #
            # replace it with this stretchBlit() call for now, and maybe
            # for good.  If so we can remove the above if statement.
            self._image.stretchBlit(srcimg._image, 
                                    (src_pos[0], src_pos[1], s_w, s_h),
                                    (dst_pos[0], dst_pos[1], d_w, d_h))
        else:
            # scaling, use stretchBlit()
            print 'use stretchBlit'
            self._image.stretchBlit(srcimg._image, 
                                    (src_pos[0], src_pos[1], s_w, s_h),
                                    (dst_pos[0], dst_pos[1], d_w, d_h))


    def clear(self, pos = (0, 0), size = (-1, -1)):
        print 'Image.clear called'
        real_size = self._image.getSize()

        if size[0] == -1:
            s_w = real_size[0]
        else:
            s_w = size[0]

        if size[1] == -1:
            s_h = real_size[1]
        else:
            s_h = size[1]

        # Is position 0,0 top left?
        self._image.setClip((pos[0], pos[1], pos[0]+s_w, pos[1]-s_h))
        self._image.clear(0,0,0,0)
        self._image.setClip()


    def draw_mask(self, maskimg, pos):
        print 'Image.draw_mask not implimented'


    def copy(self):
        print 'Image.copy called'
        return Image(copy(self._image))


    def set_font(self, font_or_fontname):
        if isinstance(font_or_fontname, Font):
            font_or_fontname = font_or_fontname._font
        return self._image.setFont(font_or_fontname)


    def get_font(self):
        return Font(self._image.getFont())


    def set_color(self, color):
        print 'set_color: %s' % str(color)

        if len(color) == 3:
            r, g, b = color
            a = 0xFF
        elif len(color) == 4:
            r, g, b, a = color
        else:
            return
        # print 'color now: %x,%x,%x,%x' % (r, g, b, a)

        try:
            self._image.setColor(r, g, b, a)
            self._color = (r, g, b, a)
        except:
            traceback.print_exc()


    def get_color(self):
        return self._color


    def draw_text(self, pos, text, color = None, font_or_fontname = None):

        if font_or_fontname:
            if isinstance(font_or_fontname, Font):
                font_or_fontname = font_or_fontname._font

            self.set_font(font_or_fontname)

        
        oldcol = self.get_color()

        if color and not color == self.get_color():
            self.set_color(color)
            self._image.drawString(text, pos[0], pos[1], DSTF_LEFT | DSTF_TOP)
            self.set_color(oldcol)
        else:
            self._image.drawString(text, pos[0], pos[1], DSTF_LEFT | DSTF_TOP)


    def draw_rectangle(self, pos, size, color, fill = True):
        oldcol = self.get_color()
        self.set_color(color)
       
        x, y = pos
        w, h = size
        if 0 in [w, h]:  
            print 'Bad rect!'
            print 'rect: %d %d %d %d' % (x, y, w, h)
            return

        self._image.setDrawingFlags(DSDRAW_BLEND)

        if fill:
            self._image.fillRectangle(x, y, w, h)
        else:
            self._image.drawRectangle(x, y, w, h)

        self.set_color(oldcol)


    def draw_ellipse(self, center, amplitude, color, fill = True):
        print 'Image.draw_ellipse called'
        if fill: fill = 1
        else: fill = 0

        self._image.setDrawingFlags(DSDRAW_BLEND)

        oldcol = self.get_color()
        self.set_color(color)
       
        self._image.drawEllipse(center, amplitude, fill)
        self.set_color(oldcol)


    def move_to_shmem(self, format = "BGRA", id = None):
        # TODO: decide if we need this, if not, remove it
        print 'Image.move_to_shmem not implimented'


    def save(self, filename, format = None):
        # TODO: find a way to save an image to file because
        #       IDirectFBImageProvider doesn't support this.
        print 'Image.save not implimented'


    def get_capabilities(self):
        return _capabilities


    def crop(self, pos, size):
        print 'Image.crop called'
         
        newsurf = dfb.createSurface(caps=self._image.getCapabilities(),
                                    width=size[0], height=size[1],
                                    pixelformat=self._image.getPixelFormat())

        newsurf.blit(self._image, 0, 0, (pos[0], pos[1], size[0], size[1]))

        self._image = newsurf


    def scale_preserve_aspect(self, size):
        print 'Image.scale_preserve_aspect called'
        self.scale(size)


    def copy_rect(self, src_pos, size, dst_pos):
        print 'Image.copy_rect called'
        self._image.blit(self._image, dst_pos[0], dst_pos[1], 
                         (src_pos[0], src_pos[1], size[0], size[1]))




class Font(base.Font):
    def __init__(self, font_or_fontdesc, color = (255, 255, 255, 255)):
        global _fonts

        if not type(font_or_fontdesc) in types.StringTypes:
            self._font = font_or_fontdesc
        else:
            (name, size) = font_or_fontdesc.split('/')

            print 'want to load font %s from %s' % (name, _fonts[name])
            try:
                self._font = dfb.createFont(_fonts[name], height=int(size))
            except:
                raise IOError, 'Failed to load font %s' % name


    def get_text_size(self, text):
        # TODO: This most definately needs to be refined.
        w = self._font.getStringWidth(text)
        h = self._font.getHeight()
        ha = self._font.getMaxAdvance()
        va = h

        return (w, h, ha, va)


    def set_color(self, color):
        pass


    def __getattr__(self, attr):
        # TODO: this needs some fixing
        if attr in ("ascent", "descent", "max_ascent", "max_descent"):
            return getattr(self._font, attr)
        return base.Font.__getattr__(self, attr)



def get_capabilities():
    return _capabilities


def open(file):
    return Image(file)


def new(size, rawdata = None, from_format = 'BGRA'):
    if from_format not in _capabilities['from-raw-formats']:
        raise ValueError, 'Unsupported raw format: %s' % from_format
    if rawdata:
        raise ValueError, 'New Image from raw data not yet supported.'

    # TODO: create a new SurfaceDescription using rawdata then pass it
    #       through Image contructor.

    return Image(dfb.createSurface(width=size[0], height=size[1]))



def add_font_path(path):
    global _font_path
    global _fonts

    _font_path.append(path)

    for font in glob.glob( os.path.join(path, '*.[T|t][T|t][F|f]')):
        fontname = os.path.basename(font).split('.')[0]
        _fonts[fontname] = font

    print 'added font path %s, fonts now:' % path
    print _fonts


def load_font(font, size):
    global _fonts

    if font.find('.'):
        font = font.split('.')[0]
    if not _fonts.get(font):
        raise IOError, 'Failed to find font %s' % font

    return Font('%s/%s' % (font, size))



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

