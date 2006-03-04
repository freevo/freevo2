# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# joystick.py - A simple joystick interface
# -----------------------------------------------------------------------------
# $Id$
#
# First draft of a joystick plugin, based on the old code
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2006 Krister Lagerstrom, Dirk Meyer, et al.
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

import kaa.notifier

import sys
import os
import select
import struct
from time import sleep

import config
from input.interface import InputPlugin

import logging
log = logging.getLogger('input')

class PluginInterface(InputPlugin):

    # Hardcoded for now to make it work at the CeBIT. This needs to
    # be a config variable.
    
    KEYMAP = {
        'button 1' : 'PLAY',
        'button 3' : 'STOP',
        'button 5' : 'EXIT',
        'button 7' : 'EXIT',
        'button 8' : 'SELECT',
        'button 6' : 'ENTER',
        'up 2'     : 'UP',
        'down 2'   : 'DOWN',
        'left 2'   : 'LEFT',
        'right 2'  : 'RIGHT' }


    def __init__(self):
        InputPlugin.__init__(self)

        # TODO: this needs to be a parameter to the plugin
        self.device_name = '/dev/input/js0'

        try:
            self.joyfd = os.open(self.device_name, os.O_RDONLY|os.O_NONBLOCK)
        except OSError:
            reason = 'Unable to open %s' % self.device_name
            return

        kaa.notifier.SocketDispatcher(self.handle).register(self.joyfd)
        self.timer = kaa.notifier.OneShotTimer(self.axis)
        self.movement = {}
        self.events = {}


    def axis(self):
        if not self.events:
            self.movement = {}
            return True
        
        axis = events = 0
        for a, l in self.events.items():
            if len(l) > events:
                events = len(l)
                axis = a
        start = self.movement[axis][0]
        stop = self.movement[axis][-1]

        if (start > 0 and stop < start) or (start < 0 and stop > start):
            return

        if axis in self.KEYMAP:
            self.post_key(self.KEYMAP[axis])

        self.events = {}
        self.movement = {}

        
    def handle( self ):
        c = os.read( self.joyfd, 8 )

        # timestamp, value, type, number
        data = struct.unpack('IhBB', c)

        button = ''
        
        if data[2] == 1 & data[1] == 1:
            # button handling
            button = 'button '+ str((data[3] + 1))
            if button in self.KEYMAP:
                self.post_key(self.KEYMAP[button])
            return True
        
        if data[2] == 2:
            # stick, this is all very ugly!!!

            if data[3] % 2 and data[1] < 0:
                button = 'up '
            elif data[3] % 2:
                button = 'down '
            elif data[1] < 0:
                button = 'left '
            else:
                button = 'right '

            button += str(data[3] / 2)
                
            if not self.events.has_key(button):
                self.events[button] = []
                self.movement[button] = []

            self.movement[button].append(data[1])

            if data[1] > -16384 and data[1] < 16384:
                return True

            self.events[button].append(data[1])
            self.timer.start(0.1)
        return True
