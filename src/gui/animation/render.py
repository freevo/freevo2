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
# Revision 1.9  2004/10/07 14:04:07  dischi
# set correct timer for notifier
#
# Revision 1.8  2004/10/06 19:24:00  dischi
# switch from rc.py to pyNotifier
#
# Revision 1.7  2004/08/27 14:15:25  dischi
# split animations into different files
#
# Revision 1.6  2004/08/23 20:35:33  dischi
# o support for displays too slow to do the animation.
# o add wait function to wait until an animation is finshed, or
#   until application fadinf animations are done
#
# Revision 1.5  2004/08/23 15:10:50  dischi
# remove callback and add wait function
#
# Revision 1.4  2004/08/23 14:28:23  dischi
# fix animation support when changing displays
#
# Revision 1.3  2004/08/22 20:06:17  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.2  2004/07/27 18:52:30  dischi
# support more layer (see README.txt in backends for details
#
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
import config, util
import gui


# python modules
import time
import copy

#external modules
import notifier

_render = None

def get_singleton():
    global _render
    return _render


def create(display):
    global _render
    _render = Render(display)


class Render:
    """
    This class/interface handles updating animation sprites

    Problems:
      How to do everything correctly so we don't end up with garbled screens.
      Currently there's probably tons of problems with this.
    """

    def __init__(self, display):
        # set the update handler to wait for osd
        self.display = display
        self.animations   = []    # all animations
        self.suspended    = []    # suspended animations
        self.__timer_id    = None  # timer id
        
    def update(self):
        """
        This is the draw method for animations
        """
        render  = []
        add     = render.append
        remove  = self.animations.remove
        i = 0

        notifier.removeTimer( self.__timer_id )
        self.__timer_id = None
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
            next = max(0, int((next - time.time()) * 1000))
            self.__timer_id = notifier.addTimer( next, self.update )


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
            notifier.removeTimer( self.__timer_id )
            self.__timer_id = None


    def killall(self):
        """
        Kills all animations
        """
        for a in copy.copy(self.animations):
            a.remove()

        notifier.removeTimer( self.__timer_id )
        self.__timer_id = None
        

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
            self.__timer_id = notifier.addTimer( 1, self.update )


    def wait(self, anim_objects=None):
        """
        wait until the given animations are finished
        """
        if anim_objects == None:
            # wait for all application show/hide animations
            anim_objects = filter(lambda a: a.application, self.animations)
        while filter(lambda a: a.running(), anim_objects):
            notifier.step( True, False )
