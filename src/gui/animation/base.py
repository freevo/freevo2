# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# base.py - The basic animation class for freevo
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Viggo Fredriksen <viggo@katatonic.org>
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

__all__ = [ 'BaseAnimation' ]

# animation imports
import render

class BaseAnimation:
    """
    Base class for animations, this should perhaps be changed to use sprites
    in the future (if one decides to go with a RenderGroup model)

     @rectstyle  : the rectangle defining the position on the screen
     @fps        : Desired fps
     @bg_update  : update the animation with background from screen
     @bg_wait    : initially wait for updated background before activating
     @bg_redraw  : set background to original screen bg when finished
    """

    def __init__(self, fps):
        self.set_fps(fps)
        self.active       = False  # Should it be updated in the poll
        self.delete       = False  # Delete from list on next poll
        self.next_update  = 0      # timestamp for next update
        self.application  = False  # True when it's for app show/hide
        self.__start_time = 0


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
        if not self.__start_time:
            self.__start_time = current_time
        if self.next_update < current_time:
            frame = int((current_time - self.__start_time) / self.interval) + 1
            self.next_update = current_time + self.interval
            self.update(frame)
            return True
        return False


    def update(self, frame):
        """
        Overload to do stuff with the surface
        """
        pass


    def finish(self):
        """
        Finish the animation and stops it. Overload to do stuff
        on the surface and call the parent function.
        """
        self.remove()


    def wait(self):
        """
        Wait for this animation to finish
        """
        render.get_singleton().wait([self])
