#if 0 /*
# -----------------------------------------------------------------------
# sdl.py - SDL input support using pygame.
# -----------------------------------------------------------------------
# $Id$
#
# This file handles pygame events and handles the keycode -> event
# mapping. You don't have to activate this plugin, it will be auto
# activated when the sdl display engine is used.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/09/27 18:40:35  dischi
# reworked input handling again
#
# Revision 1.1  2004/09/25 04:42:22  rshortt
# An SDL input handler using pygame.  This may work already but is still a
# work in progress.  Freevo still gets its input using src/gui/displays/sdl.py
# for the time being.  We need to work on universal user defined keymaps.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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
#endif

# python imports
import time
import pygame
from pygame import locals

# Freevo imports
import config
import plugin
import rc


class PluginInterface(plugin.InputPlugin):
    """
    Plugin for pygame input events
    """
    def __init__(self):
        plugin.InputPlugin.__init__(self)

        self.keymap = {}
        for key in config.KEYMAP:
            if hasattr(locals, 'K_%s' % key):
                code = getattr(locals, 'K_%s' % key)
                self.keymap[code] = config.KEYMAP[key]
            elif hasattr(locals, 'K_%s' % key.lower()):
                code = getattr(locals, 'K_%s' % key.lower())
                self.keymap[code] = config.KEYMAP[key]
            else:
                _debug_('Error: unable to find key code for %s' % key, 0)
        self.mousehidetime = time.time()
        pygame.key.set_repeat(500, 30)
        rc.register(self.handle, True, 1)


    def handle(self):
        """
        Callback to handle the pygame events.
        """
        if not pygame.display.get_init():
            return

        # Check if mouse should be visible or hidden
        mouserel = pygame.mouse.get_rel()
        mousedist = (mouserel[0]**2 + mouserel[1]**2) ** 0.5

        if mousedist > 4.0:
            pygame.mouse.set_visible(1)
            self.mousehidetime = time.time() + 1.0  # Hide the mouse in 2s
        else:
            if time.time() > self.mousehidetime:
                pygame.mouse.set_visible(0)

        # Return the next key event, or None if the queue is empty.
        # Everything else (mouse etc) is discarded.
        while 1:
            event = pygame.event.poll()

            if event.type == locals.NOEVENT:
                return

            if event.type == locals.KEYDOWN:
                if event.key in self.keymap:
                    self.post_key(self.keymap[event.key])
