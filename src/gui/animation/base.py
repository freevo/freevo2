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
# Revision 1.3  2004/08/22 20:06:17  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.2  2004/07/27 18:52:30  dischi
# support more layer (see README.txt in backends for details
#
# Revision 1.1  2004/07/22 21:11:40  dischi
# move the animation into gui, code needs update later
#
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

import pygame.time
import osd
import render

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

    active       = False  # Should it be updated in the poll
    delete       = False  # Delete from list on next poll
    next_update  = 0      # timestamp for next update


    def __init__(self, fps):
        self.set_fps(fps)


    def set_fps(self, fps):
        """
        Sets the desired fps
        """
        self.interval  = 1.0/float(fps)


    def start(self):
        """
        Starts the animation
        """
        render.get_singleton().add_animation(self)
        self.active = True
        

    def stop(self):
        """
        Stops the animation from being polled
        """
        self.active = False


    def running(self):
        """
        Return status if the animation is still running
        """
        return self.active

    
    def remove(self):
        """
        Flags the animation to be removed from the animation list
        """
        self.active = False
        self.delete = True


    def poll(self, current_time):
        if 0:
            self.next_update = 0
        if self.next_update < current_time:
            self.next_update = current_time + self.interval
            self.update()
            return True
        return False

    
    def update(self):
        """
        Overload to do stuff with the surface
        """
        pass


