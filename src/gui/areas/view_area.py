# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# view_area.py - A view area for the Freevo skin
# -----------------------------------------------------------------------------
# $Id$
#
# The file defines the ViewArea used to show an image for the current item.
# If no image is found, this area will be blank.
#
# TODO: o check if everything here is really needed and clean up if not
#       o when ItemImage from the listing area is moved to a widget use it
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

__all__ = [ 'ViewArea' ]

# area imports
from area import Area

class ViewArea(Area):
    """
    This class defines the view area.
    """
    def __init__(self):
        Area.__init__(self, 'view')
        self.info    = (None, None, None, None)
        self.content = []


    def clear(self):
        """
        Delete the shown image from screen
        """
        self.info  = (None, None, None, None)
        for c in self.content:
            c.unparent()
        self.content = []


    def update(self):
        """
        Update the view area by loading a new image or do nothing if the image
        is still the same.
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

        # FIXME: use cache here.
        image = self.imagelib.item_image(item, (width, height),
                                         self.settings.icon_dir)

        if not image:
            return

        i_w, i_h = image.width, image.height

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

        if val.rectangle:
            r.width  -= width  - i_w
            r.height -= height - i_h
            self.content.append(self.drawbox(r.x + addx, r.y + addy,
                                             r.width, r.height, r))

        self.content.append(self.drawimage(image, (x0, y0)))

