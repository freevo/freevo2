# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# image.py - basic image widget
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/09/07 18:48:57  dischi
# internal colors are now lists, not int
#
# Revision 1.3  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.2  2004/07/27 18:52:31  dischi
# support more layer (see README.txt in backends for details
#
# Revision 1.1  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
# ----------------------------------------------------------------------

from mevas.image import CanvasImage

class Image(CanvasImage):
    """
    An image object that can be drawn onto a layer
    """
    def __init__(self, image, (x, y), size=None):
        if not image:
            CanvasImage.__init__(self, (1,1))
            return
        
        CanvasImage.__init__(self, image)
        if size:
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

        self.set_pos((x, y))
