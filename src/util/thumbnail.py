# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# thumbnail.py - Thumbnail functions
# -----------------------------------------------------------------------
# $Id$
#
# The file includes functions to create and load thumbnails for images.
# The thumbnails itself are stored in the vfs
#
# For thumbnail creation, pyepeg will be used for fast jpeg thumbnails,
# other file types will be handled by the imlib2 backend of mevas. All
# thumbnails are stored at 255x255 pixel (keeping the aspect ratio).
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/09/07 18:52:51  dischi
# move thumbnail to extra file
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

__all__ = ( 'create', 'get_name', 'load' )

import os
import stat

# mevas for imlib2 support
import mevas

try:
    # pyepeg for fast jpg thumbnails
    import epeg
except ImportError:
    _debug_('epeg not found')

# pickle support
from fileops import read_pickle, save_pickle, touch

# vfs supoort for saving the thumbnail
import vfs


def read_raw_thumbnail(filename):
    """
    Read a Freevo 'raw' thumbnail. The thumbnail itself is raw data, no
    compression is used. This functions uses a lot of disc space, but is
    very fast.
    """
    f = open(filename)
    header = f.read(10)
    if not header[:3] == 'FRI':
        # raw data is a pickled imaged
        return read_pickle(filename)
    data = f.read(), (ord(header[3]), ord(header[4])), header[5:].strip(' ')
    f.close()
    return mevas.imagelib.new(data[1], data[0], data[2])


def create_raw_thumbnail(source, thumbnail):
    """
    Create a 'raw' thumbnail for the given source and store it to thumbnail.
    Return the image object.
    """
    image = mevas.imagelib.open(source)
    if image.width > 255 or image.height > 255:
        image.scale_preserve_aspect((255,255))
    f = open(thumbnail, 'w')
    if image.has_alpha:
        mode = 'RGBA'
    else:
        mode = 'RGB'
    f.write('FRI%s%s%5s' % (chr(image.width), chr(image.height), mode))
    f.write(str(image.get_raw_data(mode)))
    f.close()
    return image


def get_name(filename):
    """
    Returns the filename of the thumbnail if it exists. None if not.
    """
    if filename.endswith('.raw') or filename.endswith('.thumb.jpg'):
        return filename
    thumb = vfs.getoverlay(filename + '.raw')
    try:
        if os.stat(thumb)[stat.ST_MTIME] > os.stat(filename)[stat.ST_MTIME]:
            return thumb
        os.unlink(thumb)
    except (IOError, OSError):
        pass
    if not filename.endswith('.jpg'):
        return None
    thumb = vfs.getoverlay(filename[:-3] + 'thumb.jpg')
    try:
        if os.stat(thumb)[stat.ST_MTIME] > os.stat(filename)[stat.ST_MTIME]:
            return thumb
        os.unlink(thumb)
    except (IOError, OSError):
        pass
    return None
    

def create(filename):
    """
    Create a thumbnail for the given filename in the vfs.
    """
    print 'create', filename
    if filename.endswith('.jpg'):
        thumb = vfs.getoverlay(filename[:-3] + 'thumb.jpg')
        try:
            # epeg support for fast jpg thumbnailing
            epeg.jpg_thumbnail(filename, thumb, 255, 255)
            return mevas.imagelib.open(thumb)
        except Exception, e:
            _debug_(e)

    thumb = vfs.getoverlay(filename + '.raw')
    try:
        return create_raw_thumbnail(filename, thumb)
    except Exception, e:
        _debug_(e)
        touch(thumb)
        return None
    

def load(filename):
    """
    Return the thumbnail. Create one, if it doesn't exists.
    """
    thumb = get_name(filename)
    if thumb:
        if thumb.endswith('raw'):
            try:
                return read_raw_thumbnail(thumb)
            except:
                return None
        return mevas.imagelib.open(thumb)
    return create(filename)

