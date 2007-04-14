# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# x11.py - X11 window key input plugin
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Andreas Büsching <crunchy@tzi.de>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
# Some of the work from Andreas Büsching is moved into kaa.display
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

# python imports
import copy
import logging

# freevo imports
from freevo.ui import gui
from freevo.ui import config

# input imports
from freevo.ui.input import KEYBOARD_MAP
from interface import InputPlugin

# get logging object
log = logging.getLogger('input')

SCREENSHOT = 0

class PluginInterface(InputPlugin):
    """
    Plugin for x11 keys.
    """

    def plugin_activate(self, level):
        """
        Create eventmap on activate. FIXME: changing the setting during
        runtime has no effect.
        """
        InputPlugin.plugin_activate(self, level)
        gui.get_display()._window.signals["key_press_event"].connect(self.handle)
        self.keymap = copy.deepcopy(KEYBOARD_MAP)
        for key, mapping in config.input.keyboardmap.items():
            self.keymap[key] = mapping.upper()

        
    def handle( self, keycode ):
        """
        Callback to handle the x11 keys.
        """
        if keycode == 353:
            global SCREENSHOT
            filename = 'screenshots/screenshot-%04d.png' % SCREENSHOT
            log.info('screenshot %s' % filename)
            gui.get_display()._backing_store._image.save(filename)
            SCREENSHOT += 1
            return True

        if isinstance(keycode, int):
            log.debug('Bad keycode %s' % keycode)
            return True
        if self.keymap.has_key(keycode.upper()):
            self.post_key( self.keymap[keycode.upper()] )
        else:
            log.debug('No mapping for key %s' % keycode.upper())
        return True
