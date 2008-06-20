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
import sys
import logging

if not 'epydoc' in sys.modules:
    import pygame

# Freevo imports
from freevo.ui import gui
from freevo.ui.input import KEYBOARD_MAP
from freevo.ui import config
from freevo.ui.menu import Item
from interface import InputPlugin

# get logging object
log = logging.getLogger('input')

class PluginInterface(InputPlugin):
    """
    Plugin for pygame input events
    """

    def plugin_activate(self, level):
        """
        Active SDL input layer
        """
        InputPlugin.plugin_activate(self, level)
        # define the keymap
        self.keymap = {}
        for mapdict in (KEYBOARD_MAP, config.input.keyboardmap):
            for key, mapping in mapdict.items():
                if hasattr(pygame.locals, 'K_%s' % key):
                    code = getattr(pygame.locals, 'K_%s' % key)
                    self.keymap[code] = mapping
                elif hasattr(pygame.locals, 'K_%s' % key.lower()):
                    code = getattr(pygame.locals, 'K_%s' % key.lower())
                    self.keymap[code] = mapping
                else:
                    log.error('unable to find key code for %s' % key)

        # set mouse hiding on
        gui.get_display()._window.hide_mouse = True

        # connect to signals
        signals = gui.get_display()._window.signals
        signals['key_press_event'].connect(self.key_press_event)


    def key_press_event(self, key):
        """
        Callback when a key is pressed.
        """
        if key in self.keymap:
            self.post_key(self.keymap[key])
