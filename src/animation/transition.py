# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# transition.py - A transition animation, intended use: imageviewer
# Author: Viggo Fredriksen <viggo@katatonic.org>
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
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

from base import BaseAnimation

import pygame, random

class Transition(BaseAnimation):
    """
    This class blends two surfaces.

    Targeted to be finished within 1 second
    """
    image        = None
    finished     = False  # flag for finished animation

    surf_blend1  = None
    surf_blend2  = None


    def __init__(self, surf1, surf2, mode=-1, direction='vertical', fps=25):
        """
        @surf1: Surface to blend with
        @surf2: New surface
        @mode: effect to use
        @direction: vertical/horizontal
        """

        BaseAnimation.__init__(self, surf1.get_rect(), fps, bg_update=False)

        self.steps     = fps
        self.mode      = mode
        self.direction = direction

        self.drawfuncs = { 0: self.draw_blend_alpha,
                           1: self.draw_wipe,
                           2: self.draw_wipe_alpha }

        self.surf_blend1 = surf1.convert()
        self.surf_blend2 = surf2.convert()

        self.prepare()


    def prepare(self):

        # random effect
        if self.mode == -1:
            start = self.drawfuncs.keys()[0]
            stop  = self.drawfuncs.keys()[(len(self.drawfuncs.keys())-1)]
            self.mode = random.randrange(start, stop, 1)

            self.direction = random.choice( ['vertical', 'horizontal'] )
            self.prepare()

        # blend alpha effect
        elif self.mode == 0:
            step_size = 255.0 / self.steps
            self.index_alpha  = 0
            self.blend_alphas = [int(x*step_size) for x in range(1, self.steps+1)]
            self.blend_alphas.append(255) # The last step must be 255

        # plain wipe effect
        elif self.mode == 1:
            self.offset_x = 0
            self.offset_y = 0

            self.surface.blit(self.surf_blend1, (0, 0))

            if self.direction == 'vertical':
                step = self.rect.height / self.steps
                self.step_x = 0
                self.step_y = step
            else:
                step = self.rect.width / self.steps
                self.step_x = step
                self.step_y = 0

        # alpha wipe effect
        elif self.mode == 2:
            self.line = 0
            self.size = self.surf_blend1.get_size()
            self.surf_blend2 = self.surf_blend2.convert_alpha()
            self.fade_rows = 10
            self.fade_factor = int(256/self.fade_rows)


    def draw(self):
        if self.finished:
            return

        self.drawfuncs[self.mode]()


    def draw_wipe(self):
        """
        Plain wipe
        """
        if self.offset_x > self.rect.width:
            self.offset_x = self.rect.width
            self.finished = True

        if self.offset_y > self.rect.height:
            self.offset_y = self.rect.height
            self.finished = True


        x = self.offset_x
        y = self.offset_y
        w = self.step_x
        h = self.step_y

        if w == 0:  w = self.rect.width
        if h == 0:  h = self.rect.height

        self.surface.blit(self.surf_blend2, (x, y), (x, y, w, h))

        self.offset_x += self.step_x
        self.offset_y += self.step_y


    def draw_wipe_alpha(self):
        """
        Alpha transition wipe

        This is _very_ slow atm.

        XXX not working!
        """

        if self.line > self.size[0] - 1:
            self.finished = True

        for i in range(0, (self.line + self.fade_rows)):
            # array with alphavals
            arr = pygame.surfarray.pixels_alpha(self.surf_blend2)

            #if (arr[i] <= self.fade_factor):
            #    arr[i] = 0
            #else:
            #arr[i] -= self.fade_factor

            #for j in range(0, (self.size[0]-1)):
            #    if (arr[j][i] <= self.fade_factor):
            #        arr[j][i] = 0
            #    else:
            #        arr[j][i] -= self.fade_factor
            """
            for i in range(0, self.fade_rows):

                # Bounds check...
                if((offset - i) < 0):
                    break
                if((offset - i) > self.size[1] - 1):
                    continue
                else:
                    for j in range(0, (self.size[0]-1)):
                        if (arr[j][offset-i] <= self.fade_factor):
                            arr[j][offset-i]=0
                        else:
                            arr[j][offset-i] -= self.fade_factor
            """
        del arr

        self.line += self.fade_rows

        self.surface.blit(self.surf_blend1, (0, 0))
        self.surface.blit(self.surf_blend2, (0, 0))


    def draw_blend_alpha(self):

        alpha = self.blend_alphas[self.index_alpha]

        self.surf_blend2.set_alpha(alpha)
        self.surface.blit(self.surf_blend1, (0, 0))
        self.surface.blit(self.surf_blend2, (0, 0))

        self.index_alpha += 1

        if self.index_alpha > len(self.blend_alphas) - 1:
            self.finished = True

