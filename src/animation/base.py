# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# base.py - The basic animation class for freevo
# Author: Viggo Fredriksen <viggo@katatonic.org>
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.2  2004/05/13 12:33:42  dischi
# animation damage patch from Viggo Fredriksen
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

from pygame import Rect, Surface, constants

import pygame.time
import osd, render

class BaseAnimation:
    """
    Base class for animations, this should perhaps be changed to use sprites
    in the future (if one decides to go with a RenderGroup model)

     @rectstyle  : the rectangle defining the position on the screen (pygame)
     @fps        : Desired fps
     @bg_update  : update the animation with background from screen
     @bg_wait    : initially wait for updated background before activating
     @bg_redraw  : set background to original screen bg when finished
    """

    background   = None   # Surface Background (screen)
    surface      = None   # The Surface obj. to work with
    active       = False  # Should it be updated in the poll
    delete       = False  # Delete from list on next poll
    updates      = []     # list of updates from screen
    next_update  = 0      # timestamp for next update


    def __init__(self, rectstyle, fps=20, bg_update=True,
                 bg_wait=False, bg_redraw=False):

        self.rect      = Rect(rectstyle)
        self.bg_update = bg_update
        self.bg_wait   = bg_wait
        self.bg_redraw = bg_redraw

        self.surface = Surface( (self.rect.width,
                                 self.rect.height)).convert()

        self.set_fps(fps)


    def get_surface(self, width, height):
        """
        Helper for creating surfaces
        """
        return Surface( (width, height), 0, 32)


    def get_osd(self):
        """
        Helper for getting osd singleton
        """
        return osd.get_singleton()


    def set_fps(self, fps):
        """
        Sets the desired fps
        """
        self.interval  = int(1000.0/float(fps))


    def set_screen_background(self):
        """
        Update the background
        """
        if not self.background:
            self.background = osd.get_singleton().getsurface(rect=self.rect)
            self.updates = []

        elif len(self.updates) > 0:

            # find the topleft corner
            x = self.rect.right
            y = self.rect.bottom
            for i in self.updates:
                x = min(x, i.left)
                y = min(y, i.top)

            # find the total rect of the collisions
            upd = Rect(x, y, 0, 0)
            upd.unionall_ip(self.updates)
            self.updates = []

            x      = upd[0] - self.rect.left
            y      = upd[1] - self.rect.top
            bg_tmp = osd.get_singleton().getsurface(rect=upd)

            self.background.blit(bg_tmp, (x, y))

        self.surface.blit(self.background, (0,0))


    def get_rect(self):
        return self.rect


    def start(self):
        """
        Starts the animation
        """
        render.get_singleton().add_animation(self)
        if not self.bg_wait:
            self.active = True


    def stop(self):
        """
        Stops the animation from being polled
        """
        self.active = False


    def remove(self):
        """
        Flags the animation to be removed from the animation list
        """
        self.active = False

        # set the org. bg if we use this
        if self.bg_update:
            osd.get_singleton().putsurface(self.background,
                                           self.rect.left,
                                           self.rect.top)
            osd.get_singleton().update( [self.rect] )

        self.delete = True


    def damage(self, rectstyles=[]):
        """
        Checks if the screen background has been damaged

        Note:
            If the rect passed damages our rect, but no actual blit is done
            on osd.screen, we'll end up with a copy of our animation in our
            bg. This is BAD.
        """

        if not (self.bg_redraw or self.bg_update) or rectstyles == None:
            return

        for rect in rectstyles:
            if rect == None:
                continue

            if self.rect.colliderect(rect):
                if self.bg_wait:
                    self.active = True

                self.updates.append(self.rect.clip(rect))
                _debug_('Damaged, updating background')


    def poll(self, current_time):

        if self.next_update < current_time:
            self.next_update = current_time + self.interval

            if self.bg_update:
                self.set_screen_background()

            self.draw()
            return self.rect, self.surface


    def draw(self):
        """
        Overload to do stuff with the surface
        """
        pass


