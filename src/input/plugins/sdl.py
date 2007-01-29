# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# sdl.py - SDL input support using pygame.
# -----------------------------------------------------------------------------
# $Id$
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


# Python imports
import weakref
import pygame
import logging

# Freevo imports
import config
import gui

from menu import Item
from freevo.ui.event import *
from interface import InputPlugin

# get logging object
log = logging.getLogger('input')

class PluginInterface(InputPlugin):
    """
    Plugin for pygame input events
    """
    def __init__(self):
        InputPlugin.__init__(self)

        # define the keymap
        self.keymap = {}
        for key in config.KEYBOARD_MAP:
            if hasattr(pygame.locals, 'K_%s' % key):
                code = getattr(pygame.locals, 'K_%s' % key)
                self.keymap[code] = config.KEYBOARD_MAP[key]
            elif hasattr(pygame.locals, 'K_%s' % key.lower()):
                code = getattr(pygame.locals, 'K_%s' % key.lower())
                self.keymap[code] = config.KEYBOARD_MAP[key]
            else:
                log.error('unable to find key code for %s' % key)

        # set mouse hiding on
        gui.display._window.hide_mouse = True

        # connect to signals
        signals = gui.display._window.signals
        signals['key_press_event'].connect(self.key_press_event)


    def key_press_event(self, key):
        """
        Callback when a key is pressed.
        """
        if key in self.keymap:
            self.post_key(self.keymap[key])
