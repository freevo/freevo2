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
# Revision 1.13  2004/01/25 20:16:54  dischi
# fix mime handling
#
# Revision 1.12  2004/01/17 20:28:47  dischi
# renamed media.info to media.item
#
# Revision 1.11  2004/01/17 12:36:29  dischi
# add shadow support for image listing
#
# Revision 1.10  2004/01/01 17:41:05  dischi
# add border support for Font
#
# Revision 1.9  2003/11/29 11:27:41  dischi
# move objectcache to util
#
# Revision 1.8  2003/10/22 18:45:12  dischi
# scan for the images without fxd info
#
# Revision 1.7  2003/10/22 18:26:10  dischi
# Changes in the table code of menu items:
# o use percentage again, pixel sizes are bad because they don't scale
# o add special handling to avoid hardcoding texts in the skin file
# o new function for the skin: text_or_icon for this handling
#
# Format for this texts inside a table:
# ICON_<ORIENTATION>_<IMAGE_NAME>_<TEXT IF NO IMAGE IS THERE>
#
# Revision 1.6  2003/09/03 21:13:48  dischi
# fix aspect calc to check if correction is needed
#
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
import util

osd = osd.get_singleton()

format_imagecache = util.objectcache.ObjectCache(30, desc='format_image')
load_imagecache   = util.objectcache.ObjectCache(20, desc='load_image')


def format_image(settings, item, width, height, shadow=None, force=0):
    try:
        type = item.display_type
    except:
        try:
            type = item.info['mime'].replace('/', '_')
        except:
            type = item.type

    cname = '%s-%s-%s-%s-%s-%s-%s-%s' % (settings.icon_dir, item.image, type,
                                         item.type, width, height, shadow, force)
    if item.media and item.media.item == item:
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

        if hasattr(item, 'media') and item.media and item.media.item == item and \
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
    aspect = float(i_h)/i_w
    keep_geo = 0

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
        width =  int(float(height * i_w) / i_h)
    else:
        height = int(float(width * i_h) / i_w)

    if shadow and not shadow.visible:
        shadow = None
        
    if shadow and image.get_alpha() == None:
        cimage = pygame.Surface((width+shadow.x, height+shadow.y))
        cimage = cimage.convert_alpha()
        cimage.fill((0,0,0,0))
        cimage.fill(osd._sdlcol(shadow.color), (shadow.x, shadow.y, width, height))
        cimage.blit(pygame.transform.scale(image, (width, height)), (0,0))
        cimage.set_alpha(cimage.get_alpha(), RLEACCEL)
    else:
        cimage = pygame.transform.scale(image, (width, height))
        

#     for x in range(cimage.get_width()):
#         for y in range(cimage.get_height()):
#             cimage.set_at((x,y), (0,0,0,cimage.get_at((x,y))[-1]))


    format_imagecache[cname] = cimage, width, height
    return cimage, width, height
    

def text_or_icon(settings, string, x, width, font):
    l = string.split('_')
    if len(l) != 4:
        return string
    try:
        height = font.h
        image = os.path.join(settings.icon_dir, l[2].lower())
        if os.path.isfile(image + '.jpg'):
            image += '.jpg' 
        if os.path.isfile(image + '.png'):
            image += '.png'
        else:
            image = None
        if image:
            cname = '%s-%s-%s-%s-%s' % (image, x, l[2], width, height)
            cimage = format_imagecache[cname]
            if cimage:
                return cimage

            image = osd.loadbitmap(image)
            if not image:
                raise KeyError
            i_w, i_h = image.get_size()
            original_width = width
            if int(float(width * i_h) / i_w) > height:
                width =  int(float(height * i_w) / i_h)
            else:
                height = int(float(width * i_h) / i_w)
        
            cimage = pygame.transform.scale(image, (width, height))
            cimage.set_alpha(cimage.get_alpha(), RLEACCEL)
            x_mod = 0
            if l[1] == 'CENTER':
                x_mod = (original_width - width) / 2
            if l[1] == 'RIGHT':
                x_mod = original_width - width
            format_imagecache[cname] = x_mod, cimage
            return x_mod, cimage
    except KeyError:
        _debug_('no image %s' % l[2])
        pass

    mod_x = width - font.stringsize(l[3])
    if mod_x < 0:
        mod_x = 0
    if l[1] == 'CENTER':
        return mod_x / 2, l[3]
    if l[1] == 'RIGHT':
        return mod_x, l[3]
    return 0, l[3]
