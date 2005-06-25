# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# transition.py - Update the screen my moving/fading objects in and out
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'RANDOM', 'ALPHA_BLENDING', 'VERTICAL_WIPE', 'HORIZONAL_WIPE',
            'ALPHA_VERTICAL_WIPE', 'ALPHA_HORIZONAL_WIPE', 'Transition' ]

# python imports
import random
import logging

# animation imports
from move import *
from fade import *
import render

# get logging object
log = logging.getLogger('gui')

# settings
RANDOM = -1
ALPHA_BLENDING = 0
VERTICAL_WIPE = 1
HORIZONAL_WIPE = 2
ALPHA_VERTICAL_WIPE = 3
ALPHA_HORIZONAL_WIPE = 4


class Transition(object):
    """
    Class that contains different animations for full screen transition
    effects. It has the same functions like an animation class from the
    caller point of view.
    """
    def __init__(self, old_objects, new_objects, frames, (width, height),
                 mode = RANDOM, fps=25):

        self.anim = []
        if mode == RANDOM:
            # random mode: set a new mode based on all possible choices
            mode = random.choice([ALPHA_BLENDING, VERTICAL_WIPE,
                                  HORIZONAL_WIPE, ALPHA_VERTICAL_WIPE,
                                  ALPHA_HORIZONAL_WIPE])

        if mode == ALPHA_BLENDING:
            # alpha blending: fade out the old objects and fade in the new
            self.anim.append(FadeAnimation(old_objects, frames, 255, 0, fps))
            self.anim.append(FadeAnimation(new_objects, frames, 0, 255, fps))

        elif mode == VERTICAL_WIPE:
            # vertical wipe: move out the old objects and move in the new
            for o in new_objects:
                x, y = o.get_pos()
                o.set_pos((x, y-height))
            self.anim.append(MoveAnimation(old_objects + new_objects, VERTICAL,
                                           frames, height, fps))

        elif mode == HORIZONAL_WIPE:
            # horizontal wipe: move out the old objects and move in the new
            for o in new_objects:
                x, y = o.get_pos()
                o.set_pos((x-width, y))
            self.anim.append(MoveAnimation(old_objects + new_objects,
                                           HORIZONAL, frames, width, fps))

        elif mode == ALPHA_VERTICAL_WIPE:
            # alpha vertical wipe: fade out the old objects and move in
            # the new objects
            for o in new_objects:
                x, y = o.get_pos()
                o.set_pos((x, y-height))
            self.anim.append(FadeAnimation(old_objects, frames, 255, 0))
            self.anim.append(MoveAnimation(new_objects, VERTICAL, frames,
                                           height, fps))

        elif mode == ALPHA_HORIZONAL_WIPE:
            # alpha horizontal wipe: fade out the old objects and move in
            # the new objects
            for o in new_objects:
                x, y = o.get_pos()
                o.set_pos((x-width, y))
            self.anim.append(FadeAnimation(old_objects, frames, 255, 0))
            self.anim.append(MoveAnimation(new_objects, HORIZONAL,
                                           frames, width, fps))

        else:
            log.error('unsupported transition mode %s' % mode)


    def start(self):
        """
        Start all internal animations.
        """
        for a in self.anim:
            a.start()


    def stop(self):
        """
        Stop all internal animations.
        """
        for a in self.anim:
            a.stop()


    def remove(self):
        """
        Remove all internal animations.
        """
        for a in self.anim:
            a.remove()


    def finish(self):
        """
        finish the animation
        """
        for a in self.anim:
            a.finish()


    def running(self):
        """
        Check all internal animations if they are still running. Return True
        if at least one animation is still active.
        """
        for a in self.anim:
            if a.running():
                return True
        return False


    def wait(self):
        """
        Wait for this animation to finish
        """
        if self.anim:
            render.get_singleton().wait(self.anim)
