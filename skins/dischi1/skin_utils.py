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


osd = osd.get_singleton()

def format_image(item, width, height):
    if hasattr(item, 'display_type'):
        type = item.display_type
    else:
        type = item.type
        
    if item.image:
        image = osd.loadbitmap('thumb://%s' % item.image)

    if type == 'audio':
        m = min(height, width)
        height = m
        width  = m

    else:
        if type == 'video':
            # aspect 7:5
            i_w = 5
            i_h = 7
        else:
            i_w, i_h = image.get_size()

        if int(float(width * i_h) / i_w) > height:
            width = int(float(height * i_w) / i_h)
        else:
            height = int(float(width * i_h) / i_w)
    
    return pygame.transform.scale(image, (width, height))
    
