# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# keyboard.py - keyboard input plugin
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
from ... import core as freevo
from ... import gui
from plugin import InputPlugin

# get logging object
log = logging.getLogger('input')

KEYBOARD_MAP = {
    'F1'          : 'SLEEP',
    'HOME'        : 'MENU',
    'MENU'        : 'ENTER',
    'G'           : 'GUIDE',
    'ESCAPE'      : 'EXIT',
    'BACKSPACE'   : 'EXIT',
    'ESC'         : 'EXIT',
    'UP'          : 'UP',
    'DOWN'        : 'DOWN',
    'LEFT'        : 'LEFT',
    'RIGHT'       : 'RIGHT',
    'SPACE'       : 'SELECT',
    'RETURN'      : 'SELECT',
    'ENTER'       : 'SELECT',
    'F2'          : 'POWER',
    'F3'          : 'MUTE',
    'KP_MINUS'    : 'VOL-',
    'N'           : 'VOL-',
    'KP_PLUS'     : 'VOL+',
    'M'           : 'VOL+',
    'C'           : 'CH+',
    'V'           : 'CH-',
    '1'           : '1',
    '2'           : '2',
    '3'           : '3',
    '4'           : '4',
    '5'           : '5',
    '6'           : '6',
    '7'           : '7',
    '8'           : '8',
    '9'           : '9',
    '0'           : '0',
    'D'           : 'DISPLAY',
    'E'           : 'ENTER',
    'O'           : 'PIP_ONOFF',
    'W'           : 'PIP_SWAP',
    'I'           : 'PIP_MOVE',
    'F4'          : 'TV_VCR',
    'R'           : 'REW',
    'P'           : 'PLAY',
    'F'           : 'FFWD',
    'U'           : 'PAUSE',
    'PAUSE'       : 'PAUSE',
    'S'           : 'STOP',
    'F6'          : 'REC',
    '.'           : 'EJECT',
    'L'           : 'SUBTITLE',
    'A'           : 'LANG',
    'T'           : 'TOGGLE'
}

class PluginInterface(InputPlugin):
    """
    Plugin for x11 keys.
    """

    def plugin_activate(self, level):
        """
        Active X11 input layer
        """
        InputPlugin.plugin_activate(self, level)
        gui.signals["key-press"].connect(self.handle)
        self.keymap = copy.deepcopy(KEYBOARD_MAP)
        for key, mapping in freevo.config.input.plugin.keyboard.mapping.items():
            self.keymap[key] = mapping.upper()


    def handle(self, keycode):
        """
        Callback to handle the x11 keys.
        """
        ## print keycode
        if keycode in (276, 269025044):
            keycode = 'PAUSE'
        if keycode in (277, 269025045):
            keycode = 'STOP'
        if isinstance(keycode, int):
            log.debug('Bad keycode %s' % keycode)
            return True
        if self.keymap.has_key(keycode.upper()):
            self.post_key( self.keymap[keycode.upper()] )
        else:
            log.debug('No mapping for key %s' % keycode.upper())
        return True
