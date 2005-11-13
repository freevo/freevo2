# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# display.py - Template for Freevo displays
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines a Freevo a basic template for Freevo displays. The display
# can't be used, a real display needs to inherit from this class and a mevas
# based display.
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

# Freevo imports
import config

class Display(object):
    """
    Template for Freevo based displays. A real display needs to inherit
    from this class and a mevas display.
    """
    def __init__(self):
        self.__running = True
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
        Stop the running display
        """
        if not self.__running:
            return False
        self.freeze()
        self.__running = False
        return True

        
    def restart(self):
        """
        Restart a stopped display
        """
        if self.__running:
            return False
        
        self.thaw()
        self.__running = True
        return True
