# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# rectangle.py - basic rectangle widget
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.3  2004/08/01 10:37:08  dischi
# smaller changes to stuff I need
#
# Revision 1.2  2004/07/27 18:52:31  dischi
# support more layer (see README.txt in backends for details
#
# Revision 1.1  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
#
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

class Rectangle(CanvasImage):
    """
    A rectangle object that can be drawn onto a layer
    """
    def __init__(self, (x, y), (w, h), bgcolor, size=0, color=0, radius=0):
        CanvasImage.__init__(self, ((w, h)))

        try:
            color = self._mevascol(color)
            bgcolor = self._mevascol(bgcolor)
        except TypeError:
            pass
        
        # make sure the radius fits the box
        radius = min(radius, h / 2, w / 2)

        if not radius:
            # Simple case: rectangle without radius.
            # Drawing border + filling is very easy because there are
            # no overlapping draw areas
            if size:
                for i in range(size):
                    self.draw_rectangle((i, i), (w-2*i, h-2*i), color, 0)
            self.draw_rectangle((size, size), (w-2*size, h-2*size), bgcolor, 1)
        else:
            # Round rectangle. Simple again, if there is no alpha
            # value and no border. Else, we need do do some tricks by
            # calling this recursive
            if size:
                if bgcolor[3] == 255:
                    r, g, b, a = color
                    r = Rectangle((0,0), (w,h), (r,g,b,255), 0, color, radius)
                    self.draw_image(r, alpha=a)
                else:
                    _debug_('FIXME: round rectangle with border missing')
            r, g, b, a = bgcolor
            if a == 255:
                # no alpha, just draw
                # first set some variables, this part needs some tuning because
                # it doesn't look right to me
                w -= 2 * size
                h -= 2 * size
                amplitude = (radius, radius)
                radius += 1
                self.draw_ellipse((radius+size, radius+size), amplitude, (r,g,b), 1)
                self.draw_ellipse((size+w-radius, radius+size), amplitude, (r,g,b), 1)
                self.draw_ellipse((radius+size, size+h-radius), amplitude, (r,g,b), 1)
                self.draw_ellipse((size+w-radius, size+h-radius), amplitude, (r,g,b), 1)
                self.draw_rectangle((radius+size, size), (w-2*radius, h), (r,g,b), 1)
                self.draw_rectangle((size, radius+size), (w, h-2*radius), (r,g,b), 1)
            else:
                # alpha value :-(
                r = Rectangle((size,size), (w-2*size, h-2*size), (r,g,b,255), 0, 0, radius)
                self.draw_image(r, alpha=a)

        if x or y:
            self.set_pos((x, y))


    def _mevascol(self, col):
        """
        Convert a 32-bit TRGB color to a 4 element tuple
        """
        if col == None:
            return (0,0,0,255)
        a = 255 - ((col >> 24) & 0xff)
        r = (col >> 16) & 0xff
        g = (col >> 8) & 0xff
        b = (col >> 0) & 0xff
        c = (r, g, b, a)
        return c

