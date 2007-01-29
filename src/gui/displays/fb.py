# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fb.py - Framebuffer output
# -----------------------------------------------------------------------------
# $Id$
#
# This display also has internal support for matrox g400 cards by setting
# the fb to tv resolutions and activate the second head for tv out.
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
import os

# mevas imports
from kaa.mevas.displays.fbcanvas import FramebufferCanvas

# Freevo imports
from freevo.ui import config

# display imports
from display import Display as Base

class Display(FramebufferCanvas, Base):
    """
    Display class for framebuffer output
    """
    def __init__(self, size, default=False):
        if config.CONF.display == 'mga':
            # switch heads
            os.system('matroxset -f /dev/fb1 -m 0')
            os.system('matroxset -f /dev/fb0 -m 3')
            if config.CONF.tv == 'pal':
                # switch to PAL
                os.system('matroxset 1')
            else:
                # switch to NTSC
                os.system('matroxset -f /dev/fb0 2 2')
            # activate framebuffer with tv norm
            FramebufferCanvas.__init__(self, size, config.CONF.tv)

        else:
            # activate framebuffer without changing the resolution
            FramebufferCanvas.__init__(self, size)

        # turn off screen blanking
        os.system('setterm -blank 0')
        
        # init base display
        Base.__init__(self)


    def stop(self):
        """
        Stop the display
        """
        if Base.stop(self):
            if config.CONF.display == 'mga':
                # switch heads back
                os.system('matroxset -f /dev/fb0 -m 1')
                os.system('matroxset -f /dev/fb1 -m 0')
            del self._fb
