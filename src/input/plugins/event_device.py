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

import sys
import os
import select
import struct
import traceback
from time import sleep

import config
import plugin
import eventhandler
import rc

from input.linux_input import *
from event import *

ev = eventhandler.get_singleton()
rc = rc.get_singleton()


class PluginInterface(plugin.Plugin):

    def __init__(self):
        plugin.Plugin.__init__(self)

        self.plugin_name = 'EVDEV'
        self.device_name = config.EVDEV_DEVICE
        self.keymap = config.EVDEV_KEYMAP
        self.m_ignoreTill = 0
        self.m_ignore = config.EVDEV_REPEAT_IGNORE
        self.m_repeatRate = config.EVDEV_REPEAT_RATE
     
        if not self.device_name:
            print 'Input device plugin disabled, exiting.'
            return

        try:
            self.fd = os.open(self.device_name, 
                              os.O_RDONLY|os.O_NONBLOCK)
        except OSError:
            print 'Unable to open %s, exiting.' % self.device_name
            return
    
        print 'Using input device %s.' % self.device_name

        rc.inputs.append(self)


    def config(self):
        return [
                ( 'EVDEV_KEYMAP', 
                  {
                   KEY_POWER : 'POWER',
                   KEY_KP0   : '0',
                   KEY_KP1   : '1',
                   KEY_KP2   : '2',
                   KEY_KP3   : '3',
                   KEY_KP4   : '4',
                   KEY_KP5   : '5',
                   KEY_KP6   : '6',
                   KEY_KP7   : '7',
                   KEY_KP8   : '8',
                   KEY_KP9   : '9',
                   KEY_RED   : 'VOL+',
                   KEY_CLEAR   : '0',
                   KEY_MENU   : 'MENU',
                   KEY_MUTE   : 'MUTE',
                   KEY_VOLUMEUP   : 'RIGHT',
                   KEY_VOLUMEDOWN   : 'LEFT',
                   KEY_FORWARD   : '0',
                   KEY_EXIT   : 'EXIT',
                   KEY_CHANNELUP   : 'UP',
                   KEY_CHANNELDOWN   : 'DOWN',
                   KEY_BACK   : '0',
                   KEY_OK   : 'SELECT',
                   KEY_BLUE   : 'CH-',
                   KEY_GREEN   : 'CH+',
                   KEY_PAUSE   : 'PAUSE',
                   KEY_REWIND   : 'REW',
                   KEY_FASTFORWARD   : 'FFWD',
                   KEY_PLAY   : 'PLAY',
                   KEY_STOP   : 'STOP',
                   KEY_RECORD   : 'REC',
                   KEY_YELLOW   : 'VOL-',
                   KEY_GOTO   : 'INFO',
                   KEY_SCREEN   : 'DISPLAY',
                  }, 
                  'Default event device keymap.' ),
                ( 'EVDEV_DEVICE', '/dev/input/event0', 'Input device to use.' ),
                ( 'EVDEV_REPEAT_IGNORE', 500, 
                  'Time before first repeat (miliseconds).' ),
                ( 'EVDEV_REPEAT_RATE',   250, 
                  'Time between consecutive repeats (miliseconds).' ), ]


    def poll(self):
        command = ''    
        # _debug_('self.fd = %s' % self.fd, level=3)
        (r, w, e) = select.select([self.fd], [], [], 0)
        # _debug_('r,w,e = %s,%s,%s' % (r,w,e), level=3)
        
        if r:
            c = os.read(self.fd, 16)
#            print 'RLS: got stuff from event device'
        else: 
            return

#struct input_event {
#        struct timeval time;
#        __u16 type;
#        __u16 code;
#        __s32 value;
#};
#struct timeval {
#        time_t          tv_sec;         /* seconds */ long
#        suseconds_t     tv_usec;        /* microseconds */ long
#};

#        S_EVDATA = '2l2Hi'
        S_EVDATA = '@llHHi'

        data = struct.unpack(S_EVDATA, c)

        # make that in milliseconds
        now = (data[0] * 1000) + (data[1] / 1000)
        type = data[2]
        code = data[3]
        value = data[4]

        print '  time: %d type=%04x code=%04x value=%08x' % (now, type, code, value)

        # was it a reset?  if so, ignore
        if type == 0 :
            # print '  ignoring reset from input'
            return
        else :
            pass
        
        # I also want to ignore the "up"
        if value == 0 :
            # print '  ignoring up'
            return
        elif value == 1 :
            # set when we want to start paying attention to repeats
            self.m_ignoreTill = now + self.m_ignore
        elif value == 2 :
            if now < self.m_ignoreTill :
                print '  ignoring repeat until %d' % self.m_ignoreTill
                return
            else:
                # we let this one through, but set when we want to start
                # paying attention to the next repeat 
                self.m_ignoreTill = now + self.m_repeatRate
                pass
            pass
        else:
            pass
                
        key = self.keymap.get(code)
        if not key :
            print ' UNMAPPED KEY'
            return
        else:
            pass

        print '  sending off event %s' % key
        ev.post_key(key)

