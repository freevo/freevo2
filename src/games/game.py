#if 0 /*
# -----------------------------------------------------------------------
# game.py - Freevo module to run games. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/04/20 10:55:40  dischi
# mixer is now a plugin, too
#
# Revision 1.3  2003/02/22 07:13:19  krister
# Set all sub threads to daemons so that they die automatically if the main thread dies.
#
# Revision 1.2  2003/02/13 05:55:15  krister
# Rob Shortts bugfix for games.
#
# Revision 1.1  2002/12/09 14:23:53  dischi
# Added games patch from Rob Shortt to use the interface.py and snes support
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading, signal

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import menu       # The menu widget class
import osd        # The OSD class, used to communicate with the OSD daemon
import rc         # The RemoteControl class.
import plugin

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# Setting up the default objects:
osd        = osd.get_singleton()
rc         = rc.get_singleton()
menuwidget = menu.get_singleton()

# Module variable that contains an initialized Game() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Game()
        
    return _singleton

class Game:

    def __init__(self):
        self.thread = Game_Thread()
        self.thread.setDaemon(1)
        self.thread.start()
        self.mode = None
                         

    def play(self, item):

        self.item = item
        self.filename = item.filename 
        self.command = item.command
        self.mode = item.mode

        if not os.path.isfile(self.filename):
            osd.clearscreen()
            osd.drawstring('File "%s" not found!' % self.filename, 30, 280)
            osd.update()
            time.sleep(2.0) 
            menuwidget.refresh()
            return 0

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        # clear the screen for mame
        osd.clearscreen(color=osd.COL_BLACK)
        osd.update()

        self.thread.play_mode = self.mode
        self.thread.item  = item
        self.item  = item

        if DEBUG:
            print 'Game.play(): Starting thread, cmd=%s' % self.command
            
        self.thread.mode    = 'play'

        self.thread.command = self.command
        self.thread.mode_flag.set()
        rc.app = self.eventhandler
        

    def stop(self):
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        rc.app = None
        while self.thread.mode == 'stop':
            time.sleep(0.3)


    def eventhandler(self, event):
           return self.item.eventhandler(event, menuwidget, self.thread)

 
# ======================================================================
class GameApp(childapp.ChildApp):
        
    def kill(self):
        childapp.ChildApp.kill(self, signal.SIGINT)
        osd.update()


# ======================================================================
class Game_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None

    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
                
            elif self.mode == 'play':

                if DEBUG:
                    print 'Game_Thread.run(): Started, cmd=%s' % self.command
                
                osd.stopdisplay()     
                self.app = GameApp(self.command)
                self.app.child.wait()

                if config.OSD_SDL_EXEC_AFTER_STARTUP:
                    os.system(config.OSD_SDL_EXEC_AFTER_STARTUP)

                osd.restartdisplay()

                if self.mode == 'play':
                    rc.post_event(rc.STOP)

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'


    def cmd(self, command):
        print "In cmd going to do: " + command
        str = ''
        if command == 'config':
            str = mameKey('CONFIGMENU')
        elif command == 'pause':
            str = mameKey('PAUSE')
        elif command == 'reset':
            str = mameKey('RESET')
        elif command == 'exit':
            str = mameKey('EXIT')
        elif command == 'snapshot':
            str = mameKey('SNAPSHOT')

        self.app.write(str) 


#
# Translate an abstract remote control command to an mame
# command key
#
# I should add a hook back to whatever Item was passed here.
#
def gameKey(rcCommand):
    gameKeys = {
        'EXIT'           : '\x1b',
        }
    
    key = gameKeys.get(rcCommand, '')

    return key

