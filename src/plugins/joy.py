#if 0 /*
# -----------------------------------------------------------------------
# joy.py - A joystick control plugin for Freevo.
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
# Revision 1.4  2003/07/11 02:02:29  rshortt
# Fix for new events, we must call rc.key_event_mapper for the right event
# for what context we are in.
#
# Revision 1.3  2003/05/01 22:50:43  rshortt
# This is now a real plugin that no longer needs ENABLE_NETWORK_REMOTE to work.
#
# Revision 1.2  2003/04/27 17:28:59  rshortt
# Added the proper fileheader and some notes.
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
import rc

rc = rc.get_singleton()

DEBUG = 0

TRUE = 1
FALSE = 0


class PluginInterface(plugin.DaemonPlugin):

    def __init__(self):
        plugin.DaemonPlugin.__init__(self)

        self.plugin_name = 'JOY'
        self.device_name = ''
     
        if config.JOY_DEV == 0:
            print 'Joystick input module disabled, exiting'
            return

        self.device_name = '/dev/input/js'+str((config.JOY_DEV - 1))

        try:
            self.joyfd = os.open(self.device_name, 
                                      os.O_RDONLY|os.O_NONBLOCK)
        except OSError:
            print 'Unable to open %s, trying /dev/js%s...' % \
                  (self.device_name, self.device_name)
            self.device_name = '/dev/js'+str((config.JOY_DEV - 1))

            try:
                self.joyfd = os.open(self.device_name, 
                                          os.O_RDONLY|os.O_NONBLOCK)
            except OSError:
                print 'Unable to open %s, check modules and/or permissions' % \
                      self.device_name
                print 'exiting...'
                return
    
        print 'using joystick', config.JOY_DEV
    
        self.poll_intervall = 3
        self.poll_menu_only = FALSE


    def poll(self):
        command = ''    
        if DEBUG > 5: print 'self.joyfd = %s' % self.joyfd
        (r, w, e) = select.select([self.joyfd], [], [], 0)
        if DEBUG > 5: print 'r,w,e = %s,%s,%s' % (r,w,e)
        
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
            if ((data[3] == 1) & (data[1] < 0)):
                button = 'up'
                command = config.JOY_CMDS['up']
            if ((data[3] == 1) & (data[1] > 0)):
                button = 'down'
                command = config.JOY_CMDS['down']
            if ((data[3] == 0) & (data[1] < 0)):
                button = 'left'
                command = config.JOY_CMDS['left']
            if ((data[3] == 0) & (data[1] > 0)):
                button = 'right'
                command = config.JOY_CMDS['right']
        if command != '':
            if DEBUG: print 'Translation: "%s" -> "%s"' % (button, command)
            command = rc.key_event_mapper(command)
            if command:
                rc.post_event(command)
    

