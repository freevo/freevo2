# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# sdl.py - SDL output display
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a Freevo display based on pygame (SDL)
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
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

__all__ = [ 'Display' ]

# python imports
import pygame
import os

# mevas imports
from kaa.mevas.displays.pygamecanvas import PygameCanvas

# Freevo imports
import config
import plugin

# display imports
from display import Display as Base

class Display(PygameCanvas, Base):
    """
    Display class for SDL output
    """
    def __init__(self, size, default=False):
        PygameCanvas.__init__(self, size)
        Base.__init__(self)
        plugin.activate('input.sdl')


    def stop(self):
        """
        Stop the display
        """
        if Base.stop(self):
            pygame.display.quit()


    def restart(self):
        """
        Restart the display if it is currently stopped
        """
        if Base.restart(self):
            size = (self.width, self.height)
            self._screen  = pygame.display.set_mode(size, 0, 32)
