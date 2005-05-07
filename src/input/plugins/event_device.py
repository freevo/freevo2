#if 0 /*
# -----------------------------------------------------------------------
# event_device.py - An event device (/dev/input/eventX) plugin for Freevo.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2005/05/07 18:09:41  dischi
# move InputPlugin definition to input.interface
#
# Revision 1.8  2005/01/22 13:28:46  dischi
# remove unneeded imports
#
# Revision 1.7  2004/12/13 01:45:17  rshortt
# small cleanup and add logging
#
# Revision 1.6  2004/12/04 01:48:50  rshortt
# Comment some debug, too noisy.
#
# Revision 1.5  2004/11/04 17:40:18  dischi
# change to new notifier interface
#
# Revision 1.4  2004/10/13 20:08:25  dischi
# fix handle to match notifier callback
#
# Revision 1.3  2004/10/06 18:52:52  dischi
# use REMOTE_MAP now and switch to new notifier code
#
# Revision 1.2  2004/09/30 02:16:20  rshortt
# -turned this into an InputPlugin type
# -use the new (old) keymap
# -remove EVDEV_KEYMAP
# -set/get device keycodes
# -request exclusive access to the event device
# -add EVDEV_NAME to make it easy for users to pick it from a list, at least
#  until we autodetect it.
#
# Revision 1.1  2004/09/25 04:45:51  rshortt
# A linux event input device plugin, still a work in progress but I am using
# this for my PVR-250 remote with a custom keymap.  You may find some input
# tools to modify the keymap at http://dl.bytesex.org/cvs-snapshots/input-20040421-115547.tar.gz .
# I will incorporate the keymap viewing & loading tool into a freevo helper
# program.  plugin.activate('input.event_device')
#
# Revision 1.2  2004/09/20 01:36:15  rshortt
# Some improvements David Benoit and I worked on.
#
# Revision 1.1  2004/09/01 17:36:43  rshortt
# Event input device support.  A work in progress / proof of concept.  With this
# we can totally bypass lirc if there's an event input driver for a given
# remote.
#
#
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
import notifier

import sys
import os
import select
import struct
import fcntl
import logging
from time import sleep

import config

import input.linux_input as li
import input.evdev_keymaps as ek
from input.interface import InputPlugin

from event import *

log = logging.getLogger('input')

class PluginInterface(InputPlugin):

    def __init__(self):
        InputPlugin.__init__(self)

        self.plugin_name = 'EVDEV'
        self.device_name = config.EVDEV_DEVICE
        self._ignore_until = 0
        self.repeat_ignore = config.EVDEV_REPEAT_IGNORE
        self.repeat_rate = config.EVDEV_REPEAT_RATE
     
        try:
            self.fd = os.open(self.device_name, 
                              os.O_RDONLY|os.O_NONBLOCK)
        except OSError:
            log.error('Unable to open %s, exiting.' % self.device_name)
            return

        log.info('Using input device %s.' % self.device_name)

        exclusive = li.exclusive_access(self.fd)
        if exclusive != -1:
            log.info('Freevo granted exclusive access to %s.' % self.device_name)

        log.info('Event device name: %s' % li.get_name(self.fd))
    

        self.keymap = {}
        for key in config.REMOTE_MAP:
            if hasattr(li, 'KEY_%s' % key):
                code = getattr(li, 'KEY_%s' % key)
                self.keymap[code] = config.REMOTE_MAP[key]

        device_codes = ek.maps.get(config.EVDEV_NAME)
        for s, k in device_codes.items():
            log.debug('Adding key: 0x%04x = %3d' % (s, k))
            if not li.set_keycode(self.fd, s, k):
                log.error('Failed to set key: 0x%04x = %3d' % (s, k))

        keymap = li.get_keymap(self.fd)
        log.debug('KEYCODES:')
        for s, k in keymap.items():
            log.debug('    0x%04x = %3d' % (s, k))

        notifier.addSocket( self.fd, self.handle )


    def config(self):
        # XXX TODO: Autodetect which type of device it is so we don't need
        #           to set EVDEV_NAME, or have the user pick it from a list.
        #           Right now it is called something pretty to make it easier
        #           for users to choose the right one.

        return [
                ( 'EVDEV_NAME', 'Hauppauge PVR-250/350 IR remote', 'Long name of device.' ),
                ( 'EVDEV_DEVICE', '/dev/input/event0', 'Input device to use.' ),
                ( 'EVDEV_REPEAT_IGNORE', 400, 
                  'Time before first repeat (miliseconds).' ),
                ( 'EVDEV_REPEAT_RATE',  100, 
                  'Time between consecutive repeats (miliseconds).' ), ]


    def handle( self, socket ):
        S_EVDATA = '@llHHi'
        c = os.read(self.fd, 16)
        data = struct.unpack(S_EVDATA, c)

        # make that in milliseconds
        now = (data[0] * 1000) + (data[1] / 1000)
        type = data[2]
        code = data[3]
        value = data[4]

        # log.debug('time: %d type=%04x code=%04x value=%08x' % (now, type, code, value))

        # was it a reset?  if so, ignore
        if type == 0 :
            # log.debug('ignoring reset from input')
            return True
        
        # I also want to ignore the "up"
        if value == 0 :
            # log.debug('ignoring up')
            return True
        elif value == 1 :
            # set when we want to start paying attention to repeats
            self._ignore_until = now + self.repeat_ignore
        elif value == 2 :
            if now < self._ignore_until :
                # log.debug('ignoring repeat until %d' % self._ignore_until)
                return True
            else:
                # we let this one through, but set when we want to start
                # paying attention to the next repeat 
                self._ignore_until = now + self.repeat_rate
                
        key = self.keymap.get(code)
        if not key :
            log.warning('unmapped key: code=%s' % code)
            return True

        log.debug('posting key: %s' % key)
        self.post_key(key)

        return True
