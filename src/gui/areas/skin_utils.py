# -*- coding: iso-8859-1 -*-
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
# Revision 1.2  2004/07/24 12:21:31  dischi
# use new renderer and screen features
#
# Revision 1.1  2004/07/22 21:13:39  dischi
# move skin code to gui, update to new interface started
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


import ImageFile # from PIL
import os

import util


format_imagecache = util.objectcache.ObjectCache(30, desc='format_image')
load_imagecache   = util.objectcache.ObjectCache(20, desc='load_image')


def format_image(renderer, settings, item, width, height, force=0):
    try:
        type = item.display_type
    except:
        try:
            type = item.info['mime'].replace('/', '_')
        except:
            type = item.type

    
    key = '%s-%s-%s-%s-%s-%s-%s' % (settings.icon_dir, item.image, type,
                                      item.type, width, height, force)

    if item['rotation']:
        key = '%s-%s' % (key, item['rotation'])
            
    if item.media and item.media.item == item:
        key = '%s-%s' % (key, item.media)
        
    image = format_imagecache[key]

    if image:
        return image

    image     = None
    imagefile = None
    
    if item.image:
        if isinstance(item.image, ImageFile.ImageFile):
            image = renderer.loadbitmap(item.image)
        else:
            image = renderer.loadbitmap('thumb://%s' % item.image, load_imagecache)

        if item['rotation']:
            image = renderer.zoombitmap(image, rotation=item['rotation'])
            
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

        image = renderer.loadbitmap('thumb://%s' % imagefile, load_imagecache)

        if not image:
            return None, 0, 0

    else:
        force = 0

    if type and len(type) > 4:
        type = type[:5]
        
    i_w, i_h = image.get_size()
    aspect   = float(i_h)/i_w

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

    image = renderer.resizebitmap(image, width=width, height=height)

    format_imagecache[key] = image, width, height
    return image, width, height
    


def text_or_icon(settings, string, x, width, font, renderer):
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
            key = '%s-%s-%s-%s-%s' % (image, x, l[2], width, height)
            cimage = format_imagecache[key]
            if cimage:
                return cimage

            image = renderer.loadbitmap(image)
            if not image:
                raise KeyError
            i_w, i_h = image.get_size()
            original_width = width
            if int(float(width * i_h) / i_w) > height:
                width =  int(float(height * i_w) / i_h)
            else:
                height = int(float(width * i_h) / i_w)
        
            cimage = renderer.resizebitmap(image, width, height)

            x_mod = 0
            if l[1] == 'CENTER':
                x_mod = (original_width - width) / 2
            if l[1] == 'RIGHT':
                x_mod = original_width - width
            format_imagecache[key] = x_mod, cimage
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
