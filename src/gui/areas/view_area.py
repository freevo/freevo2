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
# Revision 1.4  2004/08/14 15:07:34  dischi
# New area handling to prepare the code for mevas
# o each area deletes it's content and only updates what's needed
# o work around for info and tvlisting still working like before
# o AreaHandler is no singleton anymore, each type (menu, tv, player)
#   has it's own instance
# o clean up old, not needed functions/attributes
#
# Revision 1.3  2004/07/24 17:49:05  dischi
# interface cleanup
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


from area import Area
from skin_utils import *


class View_Area(Area):
    """
    this call defines the view area
    """

    def __init__(self):
        Area.__init__(self, 'view')
        self.info    = (None, None, None, None)
        self.content = []


    def clear(self):
        """
        delete the shown image from screen
        """
        self.info  = (None, None, None, None)
        for c in self.content:
            self.screen.remove(c)
        self.content = []

        
    def update(self):
        """
        update the view area
        """
        item  = self.viewitem
        image = None
        try:
            image = item.image
        except:
            pass

        if not image:
            if self.content:
                self.clear()
            return

        # get layout values and calc the geometry
        content = self.calc_geometry(self.layout.content, copy_object=True)
        width   = content.width  - 2 * content.spacing
        height  = content.height - 2 * content.spacing

        # check if we need a redraw
        if self.info == (self.settings, item.image, width, height):
            return
        self.clear()
        self.info = self.settings, item.image, width, height


        x0 = 0
        y0 = 0

        try:
            val = content.types[item.type]
        except (KeyError, AttributeError):
            val = content.types['default']

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

        image, i_w, i_h = format_image(self.screen.renderer, self.settings, item,
                                       width, height)

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

        self.content.append(self.drawimage(image, (x0, y0)))

        if val.rectangle:
            r.width  -= width  - i_w
            r.height -= height - i_h
            self.content.append(self.drawbox(r.x + addx, r.y + addy, r.width, r.height, r))
