# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# dfb.py - DirectFB display
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# NOTES:
#     This is a DirectFB output mechanism using mevas' DirectFBCanvas which
#     in turn depends on pydirectfb - http://pydirectfb.sourceforge.net.
#
# -----------------------------------------------------------------------
# TODO:
#     - Add a callback for DirectFB events.
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sf.net>
# Maintainer:    Rob Shortt <rshortt@users.sf.net>
#
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
# ----------------------------------------------------------------------

# basic python imports
import time

# pydirectfb
from directfb import *

# mevas imports
from mevas.displays.directfbcanvas import DirectFBCanvas

# Freevo imports
import config


class Display(DirectFBCanvas):
    """
    Display class for DirectFB output
    """
    def __init__(self, size, default=False):
        DirectFBCanvas.__init__(self, size, config.GUI_DFB_LAYER)
        self.running = True
        self.animation_possible = True

        
    def hide(self):
        """
        Hide the output display. In most cases this does nothing since
        a simple window doesn't matter. If GUI_STOP_WHEN_PLAYING the
        ygame display will be shut down.
        """
        if config.GUI_STOP_WHEN_PLAYING:
            self.stop()


    def show(self):
        """
        Show the output window again if it is not visible
        """
        if config.GUI_STOP_WHEN_PLAYING:
            self.restart()


    def stop(self):
        """
        Stop the display
        """
        if self.running:
            self.freeze()
            self.running = False

        
    def restart(self):
        """
        Restart the display if it is currently stopped
        """
        if not self.running:
            self.thaw()
            self.running = True

        
