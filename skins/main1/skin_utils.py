#if 0
# -----------------------------------------------------------------------
# skin_utils.py - some utils for the skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2003/07/19 19:13:47  dischi
# support for item.image that is no filename but a Imaging object
#
# Revision 1.9  2003/07/13 13:44:06  dischi
# small bugfix
#
# Revision 1.8  2003/07/10 20:01:31  dischi
# support for mmpython mime types
#
# Revision 1.7  2003/07/05 09:24:32  dischi
# fixed cname cache
#
# Revision 1.6  2003/07/03 21:30:00  dischi
# minor speed changes
#
# Revision 1.5  2003/04/24 19:57:53  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.4  2003/04/21 13:25:28  dischi
# use "unknown" icon to always have an icon
#
# Revision 1.3  2003/04/20 15:01:08  dischi
# small fix
#
# Revision 1.2  2003/04/12 19:58:09  dischi
# small bugfix
#
# Revision 1.1  2003/04/06 21:19:44  dischi
# Switched to new main1 skin
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
import ImageFile

import osd
import os
import objectcache

osd = osd.get_singleton()

format_imagecache = objectcache.ObjectCache(30, desc='format_image')
load_imagecache   = objectcache.ObjectCache(20, desc='load_image')


def format_image(settings, item, width, height, force=0):
    try:
        type = item.display_type
    except:
        try:
            type = item.info.mime.replace('/', '_')
        except:
            type = item.type

    cname = '%s-%s-%s-%s-%s-%s' % (item.image, type, item.type, width, height, force)
    if item.media and item.media.info == item:
        cname = '%s-%s' % (cname, item.media)
        
    cimage = format_imagecache[cname]

    if cimage:
        return cimage

    image = None
    imagefile = None
    
    if item.image:
        if isinstance(item.image, ImageFile.ImageFile):
            image = osd.loadbitmap(item.image)
        else:
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
    
        elif os.path.isfile('%s/mimetypes/%s.png' % (settings.icon_dir, type)):
            imagefile = '%s/mimetypes/%s.png' % (settings.icon_dir, type)

        elif os.path.isfile('%s/mimetypes/%s.png' % (settings.icon_dir, item.type)):
            imagefile = '%s/mimetypes/%s.png' % (settings.icon_dir, item.type)

        elif os.path.isfile('%s/mimetypes/unknown.png' % settings.icon_dir):
            imagefile = '%s/mimetypes/unknown.png' % settings.icon_dir
            
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

    if type and len(type) > 4:
        type = type[:5]
        
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
    
