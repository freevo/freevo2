#if 0
# -----------------------------------------------------------------------
# skin_utils.py - some utils for the skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes: WIP
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2003/04/03 09:27:18  dischi
# better cache (more RAM usage but faster image menus)
#
# Revision 1.9  2003/04/02 14:14:14  dischi
# small cleanups
#
# Revision 1.8  2003/04/02 11:53:30  dischi
# small enhancements
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
# -----------------------------------------------------------------------
#endif


import pygame
from pygame.locals import *

import osd
import os
import objectcache

osd = osd.get_singleton()

format_imagecache = objectcache.ObjectCache(30, desc='format_image')
load_imagecache   = objectcache.ObjectCache(20, desc='load_image')


def format_image(settings, item, width, height, force=0):
    if hasattr(item, 'display_type'):
        type = item.display_type
    else:
        type = item.type

    cname = '%s-%s-%s-%s-%s' % (item.image, type, width, height, force)
    if hasattr(item, 'media'):
        cname = '%s-%s' % (cname, item.media)
        
    cimage = format_imagecache[cname]

    if cimage:
        return cimage

    image = None
    if item.image:
        image = load_imagecache['thumb://%s' % item.image]
        if not image:
            image = osd.loadbitmap('thumb://%s' % item.image)
            load_imagecache['thumb://%s' % item.image] = image
            
    if not image:
        if not force:
            return None, 0, 0

        if hasattr(item, 'media') and item.media and item.media.info == item and \
           os.path.isfile('%s/mimetypes/%s.png' % (settings.icon_dir, item.media.type)):
            imagefile = '%s/mimetypes/%s.png' % (settings.icon_dir, item.media.type)
            

        elif item.type == 'dir':
            if os.path.isfile('%s/mimetypes/folder_%s.png' % \
                              (settings.icon_dir, item.display_type)):
                imagefile = '%s/mimetypes/folder_%s.png' % \
                            (settings.icon_dir, item.display_type)
            else:
                imagefile = '%s/mimetypes/folder.png' % settings.icon_dir
    
        elif os.path.isfile('%s/mimetypes/%s.png' % (settings.icon_dir, item.type)):
            imagefile = '%s/mimetypes/%s.png' % (settings.icon_dir, item.type)

        if not imagefile:
            return None, 0, 0

        image = load_imagecache['thumb://%s' % imagefile]
        if not image:
            image = osd.loadbitmap('thumb://%s' % imagefile)
            load_imagecache['thumb://%s' % imagefile] = image

        if not image:
            return None, 0, 0

    else:
        force = 0

    if type == 'audio' and not force:
        m = min(height, width)
        height = m
        width  = m

    elif image:
        i_w, i_h = image.get_size()
        if type == 'video' and not force and i_w < i_h:
            # aspect 7:5
            i_w = 5
            i_h = 7

        if int(float(width * i_h) / i_w) > height:
            width = int(float(height * i_w) / i_h)
        else:
            height = int(float(width * i_h) / i_w)

    cimage = pygame.transform.scale(image, (width, height))
    cimage.set_alpha(cimage.get_alpha(), RLEACCEL)
    format_imagecache[cname] = cimage, width, height
    return cimage, width, height
    
