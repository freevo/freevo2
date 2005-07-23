# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fb.py - Framebuffer output
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'Display' ]

# python imports
import os
import tempfile

# mevas imports
from kaa.mevas.displays.fbcanvas import FramebufferCanvas

# Freevo imports
import config

# display imports
from display import Display as Base

# get logging object
log = logging.getLogger('gui')

class Display(FramebufferCanvas, Base):
    """
    Display class for SDL output
    """
    def __init__(self, size, default=False):
        if config.GUI_FB_EXEC_AFTER_STARTUP:
            os.system(config.GUI_FB_EXEC_AFTER_STARTUP)
        FramebufferCanvas.__init__(self, size)
        Base.__init__(self)


    def stop(self):
        """
        Stop the display
        """
        if Base.stop(self):
            del self._fb
            if config.GUI_FB_EXEC_AFTER_CLOSE:
                os.system(config.GUI_FB_EXEC_AFTER_CLOSE)
