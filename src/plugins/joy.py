#
# joy.py - Freevo joystick control handling.
#
# This is a standalone application that sends UDP commands to the freevo
# main app based on joypad/joystick input. Currently uses raw access to
# the Linux kernel joystick device (API v2.0).
#

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
    
    

