# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# sdl.py - SDL output display
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.11  2004/12/31 11:57:41  dischi
# renamed SKIN_* and OSD_* variables to GUI_*
#
# Revision 1.10  2004/11/27 19:07:50  dischi
# add exec before/after support
#
# Revision 1.9  2004/09/27 18:43:42  dischi
# moved input handling to inputs/plugins/sdl.py
#
# Revision 1.8  2004/09/25 15:58:44  mikeruelle
# need this import for keyboard to work
#
# Revision 1.7  2004/09/25 05:17:59  rshortt
# This was broken because I removed rc.Keyboard.  Here I add Keyboard class
# to this module and also the default keymap.  All of this stuff should actually
# go away tomorrow or so.
#
# -----------------------------------------------------------------------
#
# Freevo - A Home Theater PC framework
#
# Copyright (C) 2002 Krister Lagerstrom, et al.
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
import pygame
import os

# mevas imports
from mevas.displays.pygamecanvas import PygameCanvas

# Freevo imports
import config
import plugin

class Display(PygameCanvas):
    """
    Display class for SDL output
    """
    def __init__(self, size, default=False):
        PygameCanvas.__init__(self, size)
        self.running = True
        self.animation_possible = True
        plugin.activate('input.sdl')
        if config.GUI_SDL_EXEC_AFTER_STARTUP:
            print config.GUI_SDL_EXEC_AFTER_STARTUP
            os.system(config.GUI_SDL_EXEC_AFTER_STARTUP)
        
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
            pygame.display.quit()
            self.freeze()
            self.running = False
            if config.GUI_SDL_EXEC_AFTER_CLOSE:
                os.system(config.GUI_SDL_EXEC_AFTER_CLOSE)
        
    def restart(self):
        """
        Restart the display if it is currently stopped
        """
        if not self.running:
            self._screen  = pygame.display.set_mode((self.width, self.height), 0, 32)
            self.thaw()
            self.running = True
