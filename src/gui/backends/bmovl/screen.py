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
# Revision 1.3  2004/08/01 10:34:52  dischi
# update to changed interface
#
# Revision 1.2  2004/07/27 18:52:30  dischi
# support more layer (see README.txt in backends for details
#
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
        self.layer = Layer('content', self, True)

        if hasattr(config, 'BMOVL_OSD_VIDEO'):
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

        self.fifo    = os.open('/tmp/bmovl', os.O_WRONLY)
        self.visible = False


    def get_objects(self):
        return self.layer.objects

    
    def add(self, object):
        """
        Add an object to a specific layer.
        Hack: remove all images covering the whole screen to test transparency
        """
        if object.layer == -5:
            return
        return self.layer.add(object)

        
    def remove(self, object):
        """
        Remove an object from the screen
        """
        try:
            return self.layer.remove(object)
        except:
            pass
        

    def update(self):
        """
        Update the screen
        """
        if self.renderer.must_lock:
            # only lock s_alpha layer, because only there
            # are pixel operations (round rectangle)
            self.layer.lock()

        # Merge all update_areas
        # This is very slow, but there are transparency problems otherwise
        update_area = self.layer.update_rect

        if not update_area:
            return
        
        rect = (self.width, self.height, 0, 0)
        for x1, y1, x2, y2 in update_area:
            rect = ( min(x1, rect[0]), min(y1, rect[1]),
                     max(x2, rect[2]), max(y2, rect[3]))

        update_area            = [ rect ]
        self.layer.update_rect = update_area

        self.layer.screen.fill((0,0,0,0))
        self.layer.draw()

        if self.renderer.must_lock:
            self.layer.lock()

        blitrect = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
        surface  = self.layer.screen.subsurface(blitrect)
        _debug_('update area: %s,%s,%s,%s' % rect)

        try:
            if not self.layer.objects and self.visible:
                _debug_('hide')
                os.write(self.fifo, 'CLEAR %s %s %s %s' % (self.width, self.height, 0, 0))
                os.write(self.fifo, 'HIDE\n')
                self.visible = False
                return

            os.write(self.fifo, 'RGBA32 %d %d %d %d %d %d\n' % \
                     (surface.get_width(), surface.get_height(),
                      blitrect[0], blitrect[1], 0, 0))
            os.write(self.fifo, pygame.image.tostring(surface, 'RGBA'))

            if self.layer.objects and not self.visible:
                _debug_('show')
                os.write(self.fifo, 'SHOW\n')
                self.visible = True
        except OSError, e:
            print e

            
