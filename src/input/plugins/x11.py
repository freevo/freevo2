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

import gui
import config

from input import linux_input
from input.interface import InputPlugin

import logging
log = logging.getLogger('input')

SCREENSHOT = 0

class PluginInterface(InputPlugin):
    """
    Plugin for pygame input events
    """
    def __init__(self):
        InputPlugin.__init__(self)
        gui.display._window.signals["key_press_event"].connect(self.handle)


    def handle( self, keycode ):
        """
        Callback to handle the pygame events.
        """
        if keycode == 353:
            global SCREENSHOT
            filename = 'screenshots/screenshot-%04d.png' % SCREENSHOT
            log.info('screenshot %s' % filename)
            gui.display._backing_store._image.save(filename)
            SCREENSHOT += 1
            return True
        
        if isinstance(keycode, int):
            log.debug('Bad keycode %s' % keycode)
            return True
        if config.KEYBOARD_MAP.has_key(keycode.upper()):
            self.post_key( config.KEYBOARD_MAP[keycode.upper()] )
        else:
            log.debug('No mapping for key %s' % keycode.upper())
        return True
