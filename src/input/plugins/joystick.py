# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# joystick.py - A joystick control plugin for Freevo.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# To use this plugin make sure that your joystick is already working 
# properly and then configure JOY_DEV and JOY_CMDS in your local_conf.py.
# You will also need to have plugin.activate('joy') in your config as well.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/09/27 23:43:50  rshortt
# A few fixes but it still needs some keymap / post_key work.
#
# Revision 1.1  2004/09/27 23:10:53  rshortt
# Move the joystick plugin into the input plugins directory and renamed it
# to joystick.  plugin.activate('input.joystick')
#
# Revision 1.14  2004/08/01 10:49:47  dischi
# deactivate plugin
#
# Revision 1.13  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.12  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.11  2004/07/08 12:30:51  dischi
# only activate plugin when joystick is working
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


import sys
import os
import select
import struct
import traceback
from time import sleep

import config
import plugin
import rc

rc = rc.get_singleton()

class PluginInterface(plugin.InputPlugin):

    def __init__(self):
        plugin.InputPlugin.__init__(self)

        self.reason = config.REDESIGN_FIXME
        return

        self.plugin_name = 'JOY'
        self.device_name = ''
     
        if config.JOY_DEV == 0:
            self.reason = 'Joystick input module disabled'
            return

        self.device_name = '/dev/input/js' + str((config.JOY_DEV - 1))

        try:
            self.joyfd = os.open(self.device_name, os.O_RDONLY|os.O_NONBLOCK)
        except OSError:
            
            print 'Unable to open %s, trying /dev/js%s...' % \
                  (self.device_name, str((config.JOY_DEV - 1)))
            self.device_name = '/dev/js' + str((config.JOY_DEV - 1))

            try:
                self.joyfd = os.open(self.device_name, os.O_RDONLY|os.O_NONBLOCK)
            except OSError:
                print 'Unable to open %s, check modules and/or permissions' % \
                      self.device_name
                self.reason = 'unable to open device'
                return

        print 'using joystick', config.JOY_DEV
        
        rc.register(self.handle, True, 1)


    def handle(self):
        command = ''    
        _debug_('self.joyfd = %s' % self.joyfd, level=3)
        (r, w, e) = select.select([self.joyfd], [], [], 0)
        _debug_('r,w,e = %s,%s,%s' % (r,w,e), level=3)
        
        if r:
            c = os.read(self.joyfd, 8)
        else: 
            return

        data = struct.unpack('IhBB', c)
        if data[2] == 1 & data[1] == 1:
            button = 'button '+str((data[3] + 1))
            command = config.JOY_CMDS.get(button, '')
            sleep(0.3) # the direction pad can use lower debounce time
        if data[2] == 2:
            if ((data[3] == 1) & (data[1] < -16384)):
                button = 'up'
                command = config.JOY_CMDS['up']
            if ((data[3] == 1) & (data[1] > 16384)):
                button = 'down'
                command = config.JOY_CMDS['down']
            if ((data[3] == 0) & (data[1] < -16384)):
                button = 'left'
                command = config.JOY_CMDS['left']
            if ((data[3] == 0) & (data[1] > 16384)):
                button = 'right'
                command = config.JOY_CMDS['right']
        if command != '':
            _debug_('Translation: "%s" -> "%s"' % (button, command))
            command = rc.key_event_mapper(command)
            if command:
                eventhandler.post(command)
    

