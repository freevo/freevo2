# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# rectangle.py - basic rectangle widget
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2004/10/05 19:50:55  dischi
# Cleanup gui/widgets:
# o remove unneeded widgets
# o move window and boxes to the gui main level
# o merge all popup boxes into one file
# o rename popup boxes
#
# Revision 1.5  2004/09/07 18:48:57  dischi
# internal colors are now lists, not int
#
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
    def __init__(self, (x, y), (w, h), bgcolor=None, size=0, color=None,
                 radius=0):
        CanvasImage.__init__(self, ((w, h)))
        if x or y:
            self.set_pos((x, y))
            
        # make sure the radius fits the box
        radius = min(radius, h / 2, w / 2)

        if not radius:
            # Simple case: rectangle without radius.
            # Drawing border + filling is very easy because there are
            # no overlapping draw areas
            if size and color:
                for i in range(size):
                    self.draw_rectangle((i, i), (w-2*i, h-2*i), color, 0)
            if bgcolor:
                self.draw_rectangle((size, size), (w-2*size, h-2*size),
                                    bgcolor, 1)
            return
        
        # Round rectangle. Simple again, if there is no alpha
        # value and no border. Else, we need do do some tricks by
        # calling this recursive
        if size and color:
            if not bgcolor or len(bgcolor) == 3 or bgcolor[3] == 255:
                r = Rectangle((0,0), (w,h), color[:3], 0, None, radius)
                if len(color) == 3:
                    self.draw_image(r)
                else:
                    self.draw_image(r, alpha=color[-1])
            else:
                _debug_('FIXME: round rectangle with border missing')

        if not bgcolor:
            return

        bg = bgcolor[:3]
        if len(bgcolor) == 3 or bgcolor[3] == 255:
            # no alpha, just draw
            # first set some variables, this part needs some tuning because
            # it doesn't look right to me
            w -= 2 * size
            h -= 2 * size
            amplitude = (radius, radius)
            radius += 1
            self.draw_ellipse((radius+size, radius+size), amplitude, bg, 1)
            self.draw_ellipse((size+w-radius, radius+size), amplitude, bg, 1)
            self.draw_ellipse((radius+size, size+h-radius), amplitude, bg, 1)
            self.draw_ellipse((size+w-radius, size+h-radius), amplitude, bg, 1)
            self.draw_rectangle((radius+size, size), (w-2*radius, h), bg, 1)
            self.draw_rectangle((size, radius+size), (w, h-2*radius), bg, 1)
        else:
            # alpha value :-(
            r = Rectangle((size,size), (w-2*size, h-2*size), bg, 0, 0, radius)
            self.draw_image(r, alpha=bgcolor[3])


    def __str__(self):
        return 'Rectangle pos=%sx%s, size=%sx%s, zindex=%s' % \
               (self.get_pos() + self.get_size() + (self.get_zindex(), ))
