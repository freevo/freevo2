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
# Revision 1.7  2003/03/19 11:00:29  dischi
# cache images inside the area and some bugfixes to speed up things
#
# Revision 1.6  2003/03/15 17:25:24  dischi
# don't scale forced images
#
# Revision 1.5  2003/03/15 17:13:57  dischi
# use rom drive images for rom drive items
#
# Revision 1.4  2003/03/14 19:36:57  dischi
# some improvements for image loading
#
# Revision 1.3  2003/03/07 22:54:12  dischi
# First version of the extended menu with image support. Try the music menu
# and press DISPLAY
#
# Revision 1.2  2003/03/02 11:46:32  dischi
# Added GetPopupBoxStyle to return popup box styles to the gui
#
# Revision 1.1  2003/02/27 22:39:50  dischi
# The view area is working, still no extended menu/info area. The
# blue_round1 skin looks like with the old skin, blue_round2 is the
# beginning of recreating aubin_round1. tv and music player aren't
# implemented yet.
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
import osd
import os
import objectcache

osd = osd.get_singleton()

format_imagecache = objectcache.ObjectCache(20, desc='fomat_image')

def format_image(settings, item, width, height, force=0):
    cname = '%s-%s-%s-%s' % (item, width, height, force)
    cimage = format_imagecache[cname]

    if cimage:
        return cimage
    
    if hasattr(item, 'display_type'):
        type = item.display_type
    else:
        type = item.type

    image = None
    if item.image:
        image = osd.loadbitmap('thumb://%s' % item.image)

    if not image:
        if not force:
            return None

        if hasattr(item, 'media') and item.media and item.media.info == item and \
           os.path.isfile('%s/mimetypes/%s.png' % (settings.icon_dir, item.media.type)):
            image = '%s/mimetypes/%s.png' % (settings.icon_dir, item.media.type)
            

        elif item.type == 'dir':
            if os.path.isfile('%s/mimetypes/folder_%s.png' % \
                              (settings.icon_dir, item.display_type)):
                image = '%s/mimetypes/folder_%s.png' % \
                        (settings.icon_dir, item.display_type)
            else:
                image = '%s/mimetypes/folder.png' % settings.icon_dir
    
        elif os.path.isfile('%s/mimetypes/%s.png' % (settings.icon_dir, item.type)):
            image = '%s/mimetypes/%s.png' % (settings.icon_dir, item.type)

        if not image:
            return

        image = osd.loadbitmap('thumb://%s' % image)
        if not image:
            return

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
    format_imagecache[cname] = cimage
    return cimage
    
