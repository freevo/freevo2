# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# bmovl_renderer.py - interface to output on mplayer using bmovl
# -----------------------------------------------------------------------
# $Id$
#
# Note: This is only a test implementation with many limitations:
#       o pygame is needed to generate surfaces
#       o output is very slow
#       o you can't do anything except browsing menus
#       o when the mplayer file is finished, the screen is gone
#
#       To test this interface, set BMOVL_OSD_VIDEO in local_conf.py
#       to a video drawn in the background
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/24 12:21:06  dischi
# move renderer into backend subdir
#
# Revision 1.1  2004/07/22 21:16:01  dischi
# add first draft of new gui code
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
# -----------------------------------------------------------------------


import config
import pygame
import os

from gui.backends.sdl.screen import Screen as SDLScreen
from gui.backends.sdl.layer import Layer

class Screen(SDLScreen):
    """
    This is the Screen implementation for bmovl.
    It depends on the pygame renderer for now
    """
    def __init__(self, renderer):
        SDLScreen.__init__(self, renderer)

        self.layer['content'] = Layer('content', self.renderer, True)
        self.layer['alpha']   = Layer('alpha', self.renderer, True)
        self.layer['bg']      = Layer('bg', self.renderer, True)
        self.complete_bg      = self.renderer.screen.convert_alpha()

        print
        print 'Activating skin bmovl output'
        print 'THIS IS A TEST, DO NOT USE ANYTHING EXCEPT MENUS'
        print
        MPLAYER_SOFTWARE_SCALER = "-subfont-text-scale 15 -sws 2 -vf scale=%s:-2,"\
                                  "expand=%s:%s,bmovl=1:0:/tmp/bmovl "\
                                  "-font /usr/share/mplayer/fonts/"\
                                  "font-arial-28-iso-8859-2/font.desc" % \
                                  ( self.width, self.width, self.height )

        import childapp
        childapp.ChildApp2([config.MPLAYER_CMD] + 
                           MPLAYER_SOFTWARE_SCALER.split(' ') +
                           [config.BMOVL_OSD_VIDEO])

        self.fifo  = os.open('/tmp/bmovl', os.O_WRONLY)
        try:
            os.write(self.fifo, 'SHOW\n')
        except OSError, e:
            print e
            pass


    def add(self, layer, object):
        """
        Add an object to a specific layer.
        Hack: remove all images covering the whole screen to test transparency
        """
        if object.x1 == 0 and object.y1 == 0 and object.x2 == self.width and \
           object.y2 == self.height:
            return
        SDLScreen.add(self, layer, object)

        
    def show(self):
        """
        Update the screen
        """
        if self.renderer.must_lock:
            # only lock s_alpha layer, because only there
            # are pixel operations (round rectangle)
            self.layer['alpha'].lock()

        bg      = self.layer['bg']
        alpha   = self.layer['alpha']
        content = self.layer['content']

        # Merge all update_areas
        # This is very slow, but there are transparency problems otherwise
        update_area = bg.update_rect + alpha.update_rect + content.update_rect

        if not update_area:
            return
        
        rect = (self.width, self.height, 0, 0)
        for x1, y1, x2, y2 in update_area:
            rect = ( min(x1, rect[0]), min(y1, rect[1]),
                     max(x2, rect[2]), max(y2, rect[3]))

        update_area         = [ rect ]

        bg.update_rect      = update_area
        alpha.update_rect   = update_area
        content.update_rect = update_area

        bg.screen.fill((0,0,0,0))
        bg.draw()

        alpha.screen.fill((0,0,0,0))
        alpha.draw()

        self.complete_bg.fill((0,0,0,0))
        # and than blit only the changed parts of the screen
        for x0, y0, x1, y1 in update_area:
            self.complete_bg.blit(bg.screen, (x0, y0), (x0, y0, x1-x0, y1-y0))
            self.complete_bg.blit(alpha.screen, (x0, y0), (x0, y0, x1-x0, y1-y0))

        content.screen.fill((0,0,0,0))

        for x0, y0, x1, y1 in update_area:
            content.blit(self.complete_bg, (x0, y0), (x0, y0, x1-x0, y1-y0))

        rect = content.draw()[1]

        if self.renderer.must_lock:
            self.s_alpha.unlock()

        blitrect = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
        surface = content.screen.subsurface(blitrect)
        try:
            os.write(self.fifo, 'RGBA32 %d %d %d %d %d %d\n' % \
                     (surface.get_width(), surface.get_height(),
                      blitrect[0], blitrect[1], 0, 0))
            os.write(self.fifo, pygame.image.tostring(surface, 'RGBA'))
        except OSError, e:
            print e
