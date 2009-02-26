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

# python imports
import sys
import os
import select
import struct
from time import sleep

# kaa imports
import kaa

# freevo imports
from ... import core as freevo
from plugin import InputPlugin

import logging
log = logging.getLogger('input')

class PluginInterface(InputPlugin, freevo.ResourceHandler):

    # Hardcoded for now to make it work at the CeBIT. This needs to
    # be a config variable.
    KEYMAP = {}

    def __init__(self):
        InputPlugin.__init__(self)

        self.config = freevo.config.input.plugin.joystick

        self.device_name = self.config.device

        blocked = self.get_resources('JOYSTICK')
        if len(blocked) != 0:
            # FIXME maybe different joysticks possible?
            log.error("Joystick is allready used, can't start joystick plugin")
            return

        for mapping in self.config.events:
            self.KEYMAP[mapping.input] = mapping.event
        try:
            self.joyfd = os.open(self.device_name, os.O_RDONLY|os.O_NONBLOCK)
        except OSError:
#            reason = 'Unable to open %s' % self.device_name
            log.error('Could not open joystick interface (%s)'%self.device_name)
            self.free_resources()
            return

        self.socket_dispatcher = kaa.IOMonitor(self.handle)
        self.socket_dispatcher.register(self.joyfd)
        self.timer = kaa.OneShotTimer(self.axis)
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
    

    def can_suspend(self):
        """
        Return true since the plugin can be suspended.
        """
        return True


    def suspend(self):
        """
        Release the joystick that it can be used by others.
        """
        try:
            self.timer.stop()
            self.socket_dispatcher.unregister()
            os.close(self.joyfd)
            self.free_resources()
        except OSError:
            log.error('Could not close Filedescriptor for joystick')
            return False
        return True
        log.info('Joystick plugin suspended.')



    def resume(self):
        """
        Acquire Joystick to be used as a remote.
        """
        blocked = self.get_resources('JOYSTICK')
        if blocked == False:
            return False
        elif len(blocked) != 0:
            # FIXME maybe different joysticks possible?
            log.error("Joystick is allready used, can't start joystick plugin")
            return False

        try:
            self.joyfd = os.open(self.device_name, os.O_RDONLY|os.O_NONBLOCK)
        except OSError:
            log.error('Could not open joystick interface (%s)'%self.device_name)
            return

        self.socket_dispatcher.register(self.joyfd)
        self.movement = {}
        self.events = {}
        self.timer.start(0.1)
        log.info('Jostick plugin resumed')

