#if 0 /*
# -----------------------------------------------------------------------
# joy.py - A joystick plugin for Freevo.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# This plugin sends UDP commands to the freevo main app based on 
# joypad/joystick input.  Currently it uses raw access to the Linux kernel 
# joystick device (API v2.0).  To use this you must have set
# ENABLE_NETWORK_REMOTE = 1 and configured your joystick in  local_conf.py.
#
# -----------------------------------------------------------------------
# $Log$
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
import socket
import traceback
import threading
from time import sleep

# We need to use stuff from the main directory
sys.path += [ '..', '.' ]

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config
import plugin


class PluginInterface(plugin.DaemonPlugin):

    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.plugin_name = 'JOY'

        self.thread = joy_thread()
        self.thread.setDaemon(1)
        self.thread.start()


class joy_thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        # self.mode_flag = threading.Event()

        self.host = config.REMOTE_CONTROL_HOST
        self.port = config.REMOTE_CONTROL_PORT
     
        if config.JOY_DEV == 0:
            print 'Joystick input module disabled, exiting'
            return

        if not config.ENABLE_NETWORK_REMOTE:
            print 'You must have ENABLE_NETWORK_REMOTE = 1 in your local_conf.py!!'
            return


    def sendcmd(self, cmd):
    
        # Set up the UDP/IP connection to the Freevo main application
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.sendto(cmd, (config.REMOTE_CONTROL_HOST, config.REMOTE_CONTROL_PORT))
        except:
            print 'Freevo is down, discarding the command!\r'
        # lazy man's debounce...
        sleep(0.3)
    
    
    def run(self):
    
        # For starters, check if we are even wanted...
        if config.JOY_DEV == 0:
            print 'Joystick input module disabled, exiting'
            return
    
        joy_device = '/dev/input/js'+str((config.JOY_DEV - 1))
        try:
            j = os.open(joy_device,os.O_RDONLY|os.O_NONBLOCK)
        except OSError:
            print 'Unable to open %s, trying /dev/js%s...' % (joy_device,joy_device)
            joy_device = '/dev/js'+str((config.JOY_DEV - 1))
            try:
                j = os.open(joy_device,os.O_RDONLY|os.O_NONBLOCK)
            except OSError:
                print 'Unable to open %s, check modules and/or permissions' % joy_device
                print 'exiting...'
                return()
    
        print 'using joystick',config.JOY_DEV
        command = ''
    
        while 1:
            r,w,e=select.select([j],[],[],0)
            if r:
                c = os.read(j,8)
            data = struct.unpack('IhBB',c)
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
                print 'Translation: "%s" -> "%s"' % (button, command)
                self.sendcmd(command)
                command = ''
            sleep(0.1)
    
    

