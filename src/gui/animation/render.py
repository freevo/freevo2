# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# render.py - The render part of Freevo animation extensions
# Author: Viggo Fredriksen <viggo@katatonic.org>
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#  - Proper pausing of animations (should it still be drawn to screen?)
#  - What to do when an app like imageviewer takes the whole screen. Ex. the
#    detachbar needs to stop it's animation when this happens
#  - Update animations to support combinations of animation,
#    ex. slide the detachbar in and out of view
#  - Better handling of fps
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/22 21:11:52  dischi
# move the animation into gui, code needs update later
#
# Revision 1.3  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.2  2004/05/31 10:46:18  dischi
# update to new callback handling in rc
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


# freevo modules
import osd, config, util, rc

# pygame modules
import pygame.time

# python modules
from time      import sleep, time
import copy

_singleton = None

def get_singleton():
    global _singleton

    # don't start render for helper
    if config.HELPER:
        return

    # One-time init
    if _singleton == None:
        _singleton = util.SynchronizedObject(Render())

    return _singleton



class Render:
    """
    This class/interface handles updating animation sprites

    Problems:
      How to do everything correctly so we don't end up with garbled screens.
      Currently there's probably tons of problems with this.

    Notes:
      Perhaps we should utilize spritegroups for this, as it is supposed
      to be optimized for this kind of stuff - pluss we get alot of code
      for free. (ex. RenderUpdates). All animations objects would need to
      extend the pygame.sprite.Sprite object.
    """

    animations   = []    # all animations
    suspended    = []    # suspended animations
    osd          = None

    def __init__(self):
        # set the update handler to wait for osd
        self.update = self.update_wait


    def update_wait(self):
        """
        This is used while starting freevo
        """
        if osd._singleton == None:
            return

        if self.osd == None:
            self.osd    = osd.get_singleton()
            rc.unregister(self.update)
            self.update = self.update_enabled
            rc.register(self.update, True, 0)


    def update_enabled(self):
        """
        This is the draw method for animations
        """
        render  = []
        add     = render.append
        remove  = self.animations.remove
        i = 0

        timer   = pygame.time.get_ticks()

        for a in copy.copy(self.animations):

            # XXX something should be done to clean up the mess
            if a.delete:
                self.animations.remove(a)
                if len(self.animations) == 0:
                    # no more animations, unregister ourself to the main loop:
                    rc.unregister(self.update)
                continue

            if a.active:
                r = a.poll(timer)
                if r:
                    i += 1
                    add(r)
            # XXX something might be done to handle stopped animations
            else:
                pass

        # only invoke osd singleton if there are updates
        # since this is a potential time hog
        if len(render) > 0:
            rects = []
            for (rect, surf) in render:
                self.osd.putsurface(surf, rect.left, rect.top)
                rects.append(rect)

            if len(rects)>0:
                self.osd.update(rects)


    def damage(self, rects=[]):
        """
        This method invokes damages on animations.
        """
        for a in self.animations:
            if a.bg_redraw or a.bg_update:
                a.damage(rects)


    def kill(self, anim_object):
        """
        Kill an animation
        """

        try:
            i = self.animations.index(anim_object)
            self.animations[i].remove()
        except:
            pass
        if len(self.animations) == 0:
            # no more animations, unregister ourself to the main loop:
            rc.unregister(self.update)


    def killall(self):
        """
        Kills all animations
        """
        for a in self.animations:
            a.remove()
        rc.unregister(self.update)
        

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
            rc.register(self.update, True, 0)
