#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# Image.py - a class to define an image or icon
#                     
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2003/10/12 10:56:19  dischi
# change debug to use _debug_ and set level to 2
#
# Revision 1.4  2003/09/05 15:59:20  outlyer
# Use StringTypes instead of "StringType" since StringTypes includes unicode,
# which TV listings are sometimes in (like mine)
#
# The change to the StringTypes tuple has existed since Python 2.2 (at least)
# so it should be fine.
#
# This prevents massive explosions on mine.
#
# Revision 1.3  2003/05/02 01:09:02  rshortt
# Changes in the way these objects draw.  They all maintain a self.surface
# which they then blit onto their parent or in some cases the screen.  Label
# should also wrap text semi decently now.
#
# Revision 1.2  2003/04/24 19:56:20  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.1  2003/04/09 01:38:10  rshortt
# Initial commit of some in-progress classes.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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
#endif

import config
from GUIObject import GUIObject

class Image(GUIObject):

    def __init__(self, image_file):
        if type(image_file) in StringTypes:
            self.surface = pygame.image.load(image_file).convert_alpha()
        else:
            self.surface = image_file

        GUIObject.__init__(width = self.surface.get_width(),
                           height = self.surface.get_height())


    def set_size(self, width, height):
        aspect = (self.width / self.height)

        if(width > height):
            y = height - (self.v_margin * 2)
            x = self.height * aspect
        else:
            x = width - (self.h_margin * 2)
            y = self.width / aspect

        self.surface = pygame.transform.scale(self.icon, (x, y))

        GUIObject.set_size(width, height)


