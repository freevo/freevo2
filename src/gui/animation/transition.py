# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# transition.py - transition animations
# -----------------------------------------------------------------------
# $Id$
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

import random
from base import BaseAnimation

VERTICAL = 'VERTICAL'
HORIZONAL = 'HORIZONAL'

RANDOM = -1
ALPHA_BLENDING = 0
VERTICAL_WIPE = 1
HORIZONAL_WIPE = 2
ALPHA_VERTICAL_WIPE = 3
ALPHA_HORIZONAL_WIPE = 4


class Move(BaseAnimation):
    """
    Animation class to move 'objects' with the given pixel value
    and the given framerate on the screen
    """
    def __init__(self, objects, orientation, frames, pixel, fps=25):
        BaseAnimation.__init__(self, fps)
        self.objects     = objects
        self.orientation = orientation
        self.pixel       = pixel
        self.max_frames  = frames
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
        new_pos = int(self.frame * (float(self.pixel) / self.max_frames))
        move = new_pos - self.pos

        for o in self.objects:
            x, y = o.get_pos()
            if self.orientation == VERTICAL:
                o.set_pos((x, y + move))
            else:
                o.set_pos((x + move, y))
            
        self.pos = new_pos
        if self.frame == self.max_frames:
            self.remove()



    def finish(self):
        """
        finish the animation
        """
        self.frame = self.max_frames - 1
        self.update()
        BaseAnimation.finish(self)




class Fade(BaseAnimation):
    """
    Animation class to fade objects in or out. The alpha value of each
    object is set to 'start' and than moved to 'stop' with the given
    framerate.
    """
    def __init__(self, objects, frames, start, stop, fps=25):
        BaseAnimation.__init__(self, fps)
        self.objects     = objects
        self.max_frames  = frames
        self.frame       = 0
        self.diff        = stop - start
        self.start_alpha = start
        # make sure all objects are visible
        map(lambda o: o.show(), objects)
        if frames:
            # set start alpha value to all objects
            map(lambda o: o.set_alpha(start), objects)
        else:
            # no frames, set stop alpha value to all frames
            map(lambda o: o.set_alpha(stop), objects)
            if stop == 0:
                # if stop is 0, we can also hide the objects
                map(lambda o: o.hide(), objects)


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
        # calculate the new alpha
        alpha = self.start_alpha + int(self.frame * (float(self.diff) / self.max_frames))
        for o in self.objects:
            o.set_alpha(alpha)
        if self.frame == self.max_frames:
            self.remove()
            if self.start_alpha - self.diff == 0:
                if self.start_alpha == 255:
                    map(lambda o: o.set_alpha(255), objects)
                map(lambda o: o.hide, objects)


    def finish(self):
        """
        finish the animation
        """
        self.frame = self.max_frames - 1
        self.update()
        BaseAnimation.finish(self)


        
class Transition:
    """
    Class that contains different animations for full screen transition
    effects. It has the same functions like an animation class from the
    caller point of view.
    """
    def __init__(self, old_objects, new_objects, frames, (width, height),
                 mode = RANDOM, fps=25):

        self.animations = []
        if mode == RANDOM:
            # random mode: set a new mode based on all possible choices
            mode = random.choice([ALPHA_BLENDING, VERTICAL_WIPE, HORIZONAL_WIPE,
                                  ALPHA_VERTICAL_WIPE, ALPHA_HORIZONAL_WIPE])

        if mode == ALPHA_BLENDING:
            # alpha blending: fade out the old objects and fade in the new
            self.animations.append(Fade(old_objects, frames, 255, 0, fps))
            self.animations.append(Fade(new_objects, frames, 0, 255, fps))

        elif mode == VERTICAL_WIPE:
            # vertical wipe: move out the old objects and move in the new
            for o in new_objects:
                x, y = o.get_pos()
                o.set_pos((x, y-height))
            self.animations.append(Move(old_objects + new_objects, VERTICAL,
                                        frames, height, fps))

        elif mode == HORIZONAL_WIPE:
            # horizontal wipe: move out the old objects and move in the new
            for o in new_objects:
                x, y = o.get_pos()
                o.set_pos((x-width, y))
            self.animations.append(Move(old_objects + new_objects, HORIZONAL,
                                        frames, width, fps))

        elif mode == ALPHA_VERTICAL_WIPE:
            # alpha vertical wipe: fade out the old objects and move in the new
            for o in new_objects:
                x, y = o.get_pos()
                o.set_pos((x, y-height))
            self.animations.append(Fade(old_objects, frames, 255, 0))
            self.animations.append(Move(new_objects, VERTICAL,
                                        frames, height, fps))

        elif mode == ALPHA_HORIZONAL_WIPE:
            # alpha horizontal wipe: fade out the old objects and move in the new
            for o in new_objects:
                x, y = o.get_pos()
                o.set_pos((x-width, y))
            self.animations.append(Fade(old_objects, frames, 255, 0))
            self.animations.append(Move(new_objects, HORIZONAL,
                                        frames, width, fps))

        else:
            _debug_('Error: unsupported transition mode %s' % mode, 0)


    def start(self):
        """
        Start all internal animations.
        """
        for a in self.animations:
            a.start()

            
    def stop(self):
        """
        Stop all internal animations.
        """
        for a in self.animations:
            a.stop()

            
    def remove(self):
        """
        Remove all internal animations.
        """
        for a in self.animations:
            a.remove()

            
    def finish(self):
        """
        finish the animation
        """
        for a in self.animations:
            a.finish()


    def running(self):
        """
        Check all internal animations if they are still running. Return True
        if at least one animation is still active.
        """
        for a in self.animations:
            if a.running():
                return True
        return False
    
