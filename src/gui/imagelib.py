# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# imagelib.py - Freevo imagelib
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

__all__ = [ 'rotate', 'scale', 'load', 'item_image' ]

# python imports
import os
import stat
import logging

# mevas imagelib
import kaa.mevas

import config
import util
import theme

# get logging object
log = logging.getLogger('gui')

def _resize(image, width=None, height=None):
    """
    Resize an image (internal use)
    """
    image_w, image_h = image.width, image.height
    if width == None:
        # calculate width
        width = (height * float(image_w)) / float(image_h)
    if height == None:
        # calculate width
        height = (width * float(image_h)) / float(image_w)
    return kaa.mevas.imagelib.scale(image, (width, height))


def rotate(*arg1, **arg2):
    """
    Rotate an image
    """
    return kaa.mevas.imagelib.rotate(*arg1, **arg2)


def scale(*arg1, **arg2):
    """
    Scale an image
    """
    return kaa.mevas.imagelib.scale(*arg1, **arg2)


def load(url, size=None):
    """
    Load a bitmap and return the image object.
    If width and height are given, the image is scaled to that. Setting
    only width or height will keep aspect ratio.
    """
    if size == None:
        width, height = None, None
    else:
        width, height = size

    if not isinstance(url, (str, unicode)):
        # image already is an image object
        image = kaa.mevas.imagelib.open(url)

        # scale the image if needed
        if width != None or height != None:
            image = _resize(image, width, height)
        return image

    if url.find('/') == -1 and url.find('.') == -1:
        # this looks like a 'theme' image
        surl = theme.image(url)
        if surl:
            url = surl

    filename = os.path.abspath(url)
    
    if not os.path.isfile(filename):
        filename = os.path.join(config.IMAGE_DIR, url[8:])

    if not os.path.isfile(filename):
        log.error('Image file "%s" doesn\'t exist!' % filename)
        return None

    try:
        image = kaa.mevas.imagelib.open(filename)
    except:
        log.exception('Problem while loading image %s', url)
        image = None

    # scale the image if needed
    if width != None or height != None:
        image = _resize(image, width, height)

    return image



def item_image(item, size, icon_dir, force=False, bg=False):
    """
    Return the image for an item. This function can also return a mimetype
    image if no image is found and force is True.
    Return: image object or None
    """
    width, height = size

    try:
        type = item.display_type
    except:
        type = item.type

    image     = None
    imagefile = None

    if item.image:
        image = load(item.image)
        if item['rotation']:
            image.rotate(item['rotation'])

    if not image:
        if not force:
            return None

        if item.type == 'dir':
            if os.path.isfile('%s/mimetypes/folder_%s.png' % \
                              (icon_dir, item.display_type)):
                imagefile = '%s/mimetypes/folder_%s.png' % \
                            (icon_dir, item.display_type)
            else:
                imagefile = '%s/mimetypes/folder.png' % icon_dir

        elif item.type == 'playlist':
            if item.parent and \
                   os.path.isfile('%s/mimetypes/playlist_%s.png' % \
                                  (icon_dir, item.parent.display_type)):
                imagefile = '%s/mimetypes/playlist_%s.png' % \
                            (icon_dir, item.parent.display_type)
            else:
                imagefile = '%s/mimetypes/playlist.png' % icon_dir

        else:
            try:
                type = item.info['mime'].replace('/', '_')
            except:
                pass

            if os.path.isfile('%s/mimetypes/%s.png' % (icon_dir, type)):
                imagefile = '%s/mimetypes/%s.png' % (icon_dir, type)

            elif os.path.isfile('%s/mimetypes/%s.png' % (icon_dir, item.type)):
                imagefile = '%s/mimetypes/%s.png' % (icon_dir, item.type)

            elif os.path.isfile('%s/mimetypes/unknown.png' % icon_dir):
                imagefile = '%s/mimetypes/unknown.png' % icon_dir

        image = load(imagefile)

        if not image:
            return None

    if type and len(type) > 4:
        type = type[:5]

    i_w = image.width
    i_h = image.height
    aspect = float(i_h)/i_w

    if type == 'audio' and aspect < 1.3 and aspect > 0.8:
        # this is an audio cover
        m = min(height, width)
        i_w = m
        i_h = m

    elif type == 'video' and aspect > 1.3 and aspect < 1.6:
        # video cover, set aspect 7:5
        i_w = 5
        i_h = 7

    if int(float(width * i_h) / i_w) > height:
        width = int(float(height * i_w) / i_h)
    else:
        height = int(float(width * i_h) / i_w)

    image.scale((width, height))
    return image
