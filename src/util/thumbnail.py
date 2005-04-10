# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# thumbnail.py - Thumbnail functions
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines some helper functions for creating thumbnails for faster
# image access. The thumbnails are stored in the vfs and have a max size
# of 255x255 pixel. 
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

__all__ = ( 'create', 'get_name', 'load' )

# python imports
import os
import logging
import stat

# mevas for imlib2 support
import mevas

# freevo utils
import fileops
import vfs
from callback import *

# the logging object
log = logging.getLogger('util')

# list for thumbnails to create in bg
_create_jobs = []


def get_name(filename):
    """
    Returns the filename of the thumbnail if it exists. None if not.
    """
    s = os.stat(filename)
    if s[stat.ST_SIZE] < 30000:
        return filename
    base = filename[:filename.rfind('.')]
    if base.endswith('.thumb'):
        return filename
    thumb = vfs.getoverlay(base + '.thumb' + filename[filename.rfind('.'):])
    if not os.path.isfile(thumb):
        return None

    if os.stat(thumb)[stat.ST_MTIME] > s[stat.ST_MTIME]:
        return thumb
    os.unlink(thumb)
    return None


def create(filename, check_overlay=True):
    """
    Create a thumbnail for the given filename in the vfs.
    """
    if check_overlay and \
           not os.path.isdir(os.path.dirname(vfs.getoverlay(filename))):
        os.makedirs(os.path.dirname(vfs.getoverlay(filename)))
    base  = filename[:filename.rfind('.')]
    thumb = vfs.getoverlay(base + '.thumb' + filename[filename.rfind('.'):])
    if filename in _create_jobs:
        _create_jobs.remove(filename)
        if _create_jobs:
            call_later(10, create, _create_jobs[0])
    try:
        return mevas.imagelib.thumbnail(filename, thumb, (255, 255))
    except:
        return None


def load(filename, bg=False):
    """
    Return the thumbnail. Create one, if it doesn't exists.
    """
    try:
        thumb = get_name(filename)
    except OSError:
        return None
    if thumb:
        return mevas.imagelib.open(thumb)
    if not bg:
        return create(filename)
    if filename in _create_jobs:
        return
    _create_jobs.append(filename)
    call_later(10, create, _create_jobs[0])
    return None
