# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# render.py - The render part
# -----------------------------------------------------------------------------
# $Id$
#
# Todo:
#  - Proper pausing of animations (should it still be drawn to screen?)
#  - What to do when an app like imageviewer takes the whole screen. Ex. the
#    detachbar needs to stop it's animation when this happens
#  - Update animations to support combinations of animation,
#    ex. slide the detachbar in and out of view
#  - Better handling of fps
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Viggo Fredriksen <viggo@katatonic.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
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


# python imports
import time
import copy

# kaa imports
import kaa

# global render object
_render = None

def get_singleton():
    global _render
    return _render


def create(display):
    global _render
    _render = Render(display)


class Render(object):
    """
    This class/interface handles updating animation sprites

    Problems:
      How to do everything correctly so we don't end up with garbled screens.
      Currently there's probably tons of problems with this.
    """
    def __init__(self, display):
        # set the update handler to wait for osd
        self.display = display
        self.update_timer = kaa.OneShotTimer(self.update)
        self.animations = []    # all animations
        self.suspended  = []    # suspended animations


    def update(self):
        """
        This is the draw method for animations
        """
        render  = []
        add     = render.append
        remove  = self.animations.remove
        i = 0

        timer = time.time()
        next  = 0

        update_screen = False
        for a in copy.copy(self.animations):
            # XXX something should be done to clean up the mess
            if a.delete:
                a.active = False
                self.animations.remove(a)
                continue

            if a.active:
                # no animation possible, finish the animation at once
                if not self.display.animation_possible:
                    a.finish()
                    update_screen = True
                else:
                    update_screen = a.poll(timer) or update_screen
                    next = min(next, a.next_update) or a.next_update
            # XXX something might be done to handle stopped animations
            else:
                pass

        if update_screen:
            self.display.update()
        if len( self.animations ):
            next = max(0, int((next - time.time())))
            self.update_timer.start(next)
    

    def kill(self, anim_object):
        """
        Kill an animation
        """

        try:
            i = self.animations.index(anim_object)
            self.animations[i].remove()
        except:
            pass
        if len( self.animations ) == 0:
            # no more animations, unregister ourself to the main loop:
            self.update_timer.stop()


    def killall(self):
        """
        Kills all animations
        """
        for a in copy.copy(self.animations):
            a.remove()
        self.update_timer.stop()


    def suspendall(self):
        """
        Suspends all animations
        """
        for a in self.animations:
            if a.active:
                a.active = False
                self.suspended.append(a)


    def restartall(self):
        """
        Restarts all suspended animations
        """
        for a in self.suspended:
            a.active = True

        self.suspended = []


    def add_animation(self, anim_object):
        """
        Add an animation to our list
        """
        self.animations.append(anim_object)
        if len(self.animations) == 1:
            # first animation, register ourself to the main loop:
            self.update_timer.start(0)


    def wait(self, anim_objects=None):
        """
        wait until the given animations are finished
        """
        if anim_objects == None:
            # wait for all application show/hide animations
            anim_objects = filter(lambda a: a.application, self.animations)
        while filter(lambda a: a.running(), anim_objects):
            kaa.main.step( True, False )
