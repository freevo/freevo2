# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# image.py - basic image widget
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
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


from base import GUIObject

class Image(GUIObject):
    """
    An image object that can be drawn onto a layer
    """
    def __init__(self, x1, y1, x2, y2, image):
        GUIObject.__init__(self, x1, y1, x2, y2)
        self.image = image


    def draw(self, rect=None):
        if not self.screen:
            raise TypeError, 'no screen defined for %s' % self
        if not rect:
            _debug_('full update')
            self.screen.blit(self.image, (self.x1, self.y1))
        else:
            x1, y1, x2, y2 = rect
            if not (self.x2 < x1 or self.y2 < y1 or self.x1 > x2 or self.y1 > y2):
                self.screen.blit(self.image, rect[:2],
                                 (x1-self.x1, y1-self.y1, x2-x1, y2-y1))


    def __cmp__(self, o):
        try:
            return self.x1 != o.x1 or self.y1 != o.y1 or self.x2 != o.x2 or \
                   self.y2 != o.y2 or self.image != o.image
        except Exception, e:
            print e
            return 1
