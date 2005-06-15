#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# x11.py
# 
# Author:   <crunchy@tzi.de>
# 
# x11
# 
# $Id$
# 
# Copyright (C) 2004 Andreas Büsching <crunchy@tzi.de>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import notifier

import gui
import config

from input import linux_input
from input.interface import InputPlugin

import logging
log = logging.getLogger('input')

class PluginInterface(InputPlugin):
    """
    Plugin for pygame input events
    """
    def __init__(self):
        InputPlugin.__init__(self)

        self.keymap = {}
        for key in config.KEYBOARD_MAP:
            if hasattr(linux_input, 'KEY_%s' % key):
                code = getattr(linux_input, 'KEY_%s' % key)
                self.keymap[code] = config.KEYBOARD_MAP[key]
            elif key == 'ESCAPE':
                self.keymap[ linux_input.KEY_ESC ] = config.KEYBOARD_MAP[ key ]
            elif key == 'RETURN':
                self.keymap[ linux_input.KEY_ENTER ] = \
                             config.KEYBOARD_MAP[ key ]
            elif key == 'PERIOD':
                self.keymap[ linux_input.KEY_DOT ] = config.KEYBOARD_MAP[ key ]
            elif key == 'KP_MINUS':
                self.keymap[ linux_input.KEY_KPMINUS ] = \
                             config.KEYBOARD_MAP[ key ]
            elif key == 'KP_PLUS':
                self.keymap[ linux_input.KEY_KPPLUS ] = \
                             config.KEYBOARD_MAP[ key ]
            else:
                log.error('unable to find key code for %s' % key)
        display = gui.display._display
        display.input_callback = self.handle
        notifier.addSocket( display.socket, display.handle_events )

 
    def handle( self, keycode ):
        """
        Callback to handle the pygame events.
        """
        # DO NOT ASK!!!!
        if keycode > 96: keycode += 5
        else: keycode -= 8
        if keycode > 105: keycode -= 1
        
        if keycode in self.keymap:
            self.post_key( self.keymap[ keycode ] )
        return True
