# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# move.py - Animation to move objects on the screen
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/08/27 14:15:25  dischi
# split animations into different files
#
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

__all__ = [ 'VERTICAL', 'HORIZONAL', 'MoveAnimation' ]

VERTICAL  = 'VERTICAL'
HORIZONAL = 'HORIZONAL'

from base import BaseAnimation

class MoveAnimation(BaseAnimation):
    """
    Animation class to move 'objects' with the given pixel value
    and the given framerate on the screen
    """
    def __init__(self, objects, orientation, frames, pixel, fps=25):
        BaseAnimation.__init__(self, fps)
        self.objects     = objects
        self.orientation = orientation
        self.pixel       = pixel
        self.max_frames  = max(frames, 1)
        self.frame       = 0
        self.pos         = 0
        # make sure all objects are visible
        map(lambda o: o.show(), objects)


    def update(self):
        """
        update the animation
        """
        self.frame += 1
        if not self.max_frames:
            # if there are no frames, remove the
            # animation, it can't run
            self.remove()
            return

        # calculate the new position
        new_pos = int(self.frame * (float(self.pixel) / self.max_frames))
        # move objects
        for o in self.objects:
            if self.orientation == VERTICAL:
                o.move_relative((0, new_pos - self.pos))
            else:
                o.move_relative((new_pos - self.pos, 0))
        # store new position
        self.pos = new_pos
        # remove animation when done
        if self.frame == self.max_frames:
            self.remove()


    def finish(self):
        """
        finish the animation
        """
        self.frame = self.max_frames - 1
        self.update()
        BaseAnimation.finish(self)
