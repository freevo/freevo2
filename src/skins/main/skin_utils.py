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
# Revision 1.5  2003/08/24 05:57:50  gsbarbieri
# Try to use playlist icon based on parent directory display_type, so in a
# music dir, you got playlist_audio.
#
# Revision 1.4  2003/08/23 19:25:46  dischi
# some scaling fixes
#
# Revision 1.3  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
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

    cname = '%s-%s-%s-%s-%s-%s-%s' % (settings.icon_dir, item.image, type,
                                      item.type, width, height, force)
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
    
        elif item.type == 'playlist':
            if item.parent and os.path.isfile('%s/mimetypes/playlist_%s.png' % \
                                              (settings.icon_dir, item.parent.display_type)):
                imagefile = '%s/mimetypes/playlist_%s.png' % \
                            (settings.icon_dir, item.parent.display_type)
            else:
                imagefile = '%s/mimetypes/playlist.png' % settings.icon_dir

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
        
    i_w, i_h = image.get_size()
    aspect = max(float(i_h)/i_w, float(i_w)/i_h)
    keep_geo = 0

    if type == 'audio' and aspect < 1.3:
        # this is an audio cover
        m = min(height, width)
        i_w = m
        i_h = m
        
    elif type == 'video' and aspect > 1.3:
        # video cover, set aspect 7:5
        i_w = 5
        i_h = 7
        
    if int(float(width * i_h) / i_w) > height:
        width =  int(float(height * i_w) / i_h)
    else:
        height = int(float(width * i_h) / i_w)
        
    cimage = pygame.transform.scale(image, (width, height))
    cimage.set_alpha(cimage.get_alpha(), RLEACCEL)
    format_imagecache[cname] = cimage, width, height
    return cimage, width, height
    
