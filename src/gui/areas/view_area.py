# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# view_area.py - A view area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:13:39  dischi
# move skin code to gui, update to new interface started
#
# Revision 1.7  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.6  2004/02/04 19:05:36  dischi
# remove bad log message
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


from area import Skin_Area
from skin_utils import *

class View_Area(Skin_Area):
    """
    this call defines the view area
    """

    def __init__(self):
        Skin_Area.__init__(self, 'view')
        self.image = None


    def update_content_needed(self):
        """
        check if the content needs an update
        """
        item = self.viewitem
        image = None

        if hasattr(item, 'image') and item.image:
            image = item.image

        return image != self.image
    

    def update_content(self):
        """
        update the view area
        """

        item = self.viewitem
        
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=True)

        if hasattr(item, 'type') and content.types.has_key(item.type):
            val = content.types[item.type]
        else:
            val = content.types['default']

        if hasattr(item, 'image') and item.image:
            self.image = item.image
        else:
            self.image = None
            return

        x0 = 0
        y0 = 0

        width  = content.width - 2*content.spacing
        height = content.height - 2*content.spacing

        
        if val.rectangle:
            r = self.get_item_rectangle(val.rectangle, width, height)[2]

            if r.x < 0:
                x0 -= r.x
                r.x = 0
            
            if r.y < 0:
                y0 -= r.y
                r.y = 0
            
            if r.x + r.width > x0 + width:
                r.width, width = width, width - (r.width - width)

            if r.y + r.height > y0 + height:
                r.height, height = height, height - (r.height - height)

        addx = content.x + content.spacing
        addy = content.y + content.spacing

        image, i_w, i_h = format_image(self.settings, item, width, height)

        if not image:
            return
        
        if content.align == 'center' and i_w < width:
            addx += (width - i_w) / 2

        if content.align == 'right' and i_w < width:
            addx += width - i_w
            
        if content.valign == 'center' and i_h < height:
            addy += (height - i_h) / 2

        if content.valign == 'bottom' and i_h < height:
            addy += height - i_h

        x0 += addx
        y0 += addy

        self.drawimage(image, (x0, y0))

        if val.rectangle:
            r.width -= width - i_w
            r.height -= height - i_h
            self.drawroundbox(r.x + addx, r.y + addy, r.width, r.height, r)
