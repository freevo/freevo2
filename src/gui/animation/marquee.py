# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# marquee.py - A marquee animation, intended use: selected text
# Author: Viggo Fredriksen <viggo@katatonic.org>
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:11:40  dischi
# move the animation into gui, code needs update later
#
# Revision 1.2  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.1  2004/04/25 11:23:58  dischi
# Added support for animations. Most of the code is from Viggo Fredriksen
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
# ----------------------------------------------------------------------- */


from base   import BaseAnimation
from pygame import Rect

class Marquee(BaseAnimation):
    """
    This class animates a surface like a marquee.

    Nothing fancy, just scrolls it back and forth, takes a pause
    when returning to ground zero. This is just intended as a demo
    for testing the rendering.
    """
    smoothfactor = 0.1
    image        = None


    def __init__(self, rectstyle, surface, step_x=1, fps=25, init_sleep=-1,
                 bg_update=True, bg_wait=False, bg_redraw=False):

        BaseAnimation.__init__(self, rectstyle, fps, bg_update, bg_wait, bg_redraw)

        self.image  = surface
        self.step_x = step_x

        self.w, self.h = surface.get_size()
        self.animrect  = Rect( (0, 0, self.rect.width, self.rect.height) )


    def draw(self):
        if self.w < self.rect.width:
            self.surface.blit(self.image, (0,0))
            return

        ### move and blit
        self.animrect.move_ip(int(self.step_x * self.smoothfactor), 0)
        self.surface.blit(self.image, (0,0), self.animrect)

        ### recalculate for next pass
        if self.smoothfactor < float(1):
            self.smoothfactor *= 1.1
            if self.smoothfactor > float(1):
                self.smoothfactor = 1


        # at bounds, change direction
        if self.animrect.right > self.w or self.animrect.left < 0:
            self.smoothfactor = 0.08
            if self.step_x < 0:
                self.animrect.left  = 0
                self.sleep = True
            else:
                self.animrect.right = self.w

            self.step_x = - self.step_x
