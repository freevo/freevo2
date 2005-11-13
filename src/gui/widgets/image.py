# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# image.py - basic image widget
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines an image widget to use on a container or display. Besides
# the normal CanvasImage this class can also auto-resize the image and draw
# a shadow behind the image.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file doc/CREDITS for a complete list of authors.
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

import gui.imagelib
from kaa.mevas.image import CanvasImage

class Image(CanvasImage):
    """
    An image that can be added to a container or display. It can be created
    with an imagelib image or a filename and can optional position or resize
    the image or create a shadow behind it.
    """
    def __init__(self, image, pos=None, size=None, shadow=None):
        """
        Create the image.
        Parameter description:
        image    an imagelib image, string or list (image, (width, height))
        pos      postion of the image on the parent
        size     if set, the image will be scalled the given size. If width or
                 height is None or -1, the image will be scalled to keep the
                 aspect ratio
        shadow   a tripple x,y,color defining the attributes of the shadow
                 that will be added behind the image
        """
        if isinstance(image, (str, unicode)):
            # load image
            image = gui.imagelib.load(image)

        if isinstance(image, (list, tuple)):
            # load image
            image = gui.imagelib.load(image[0], image[1])

        if not image:
            # invalid image, return 1x1 empty space
            CanvasImage.__init__(self, (1,1))
            return

        if shadow:
            # shadow used, drop a shadow at x,y with the given color
            sx, sy, scolor = shadow
            CanvasImage.__init__(self, (image.width + sx,
                                        image.height + sy))
            # draw shadow
            self.draw_rectangle((sx, sy), (image.width, image.height),
                                scolor, 1)
            # draw image
            self.draw_image(image)
        else:
            # CanvasImage is only the image itself
            CanvasImage.__init__(self, image)

        if size:
            # resize the image
            width, height = size
            # check width and height for scaling
            if width == None or width == -1:
                # calculate width
                width = (height * float(image_w)) / float(image_h)
            if height == None or height == -1:
                # calculate height
                height = (width * float(image_h)) / float(image_w)
            if width != self.image.width or height != self.image.height:
                self.image.scale((width, height))

        if pos:
            # set position on parent
            self.set_pos(pos)


    def __str__(self):
        return 'Image pos=%sx%s, size=%sx%s, zindex=%s' % \
               (self.get_pos() + self.get_size() + (self.get_zindex(), ))
