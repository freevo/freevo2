#if 0 /*
# -----------------------------------------------------------------------
# xine.py - the Freevo XINE module for video
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/07/20 19:56:25  dischi
# small fixes
#
# Revision 1.1  2003/07/20 17:50:24  dischi
# Very basic Xine support. By loading this plugin and setting XINE_COMMAND
# in the local_conf.py, xine will be used as DVD player when you hit PLAY
# on the item (or SELECT it). In all other cases, mplayer will be taken.
# Xine is only used for DVDnav support. There is no eventhandler, xine
# must be in the foreground and the keys and lirc commands are taken from
# Xine, not Freevo. Only testet with X, I don't know if framebuffer works
# at all.
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


import time, os
import threading, signal

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import rc         # The RemoteControl class.
import skin

from event import *
import plugin

# RegExp
import re

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# contains an initialized Xine() object
xine = None

class PluginInterface(plugin.Plugin):
    """
    Xine plugin for the video player. Use xine to play all video
    files.
    """
    def __init__(self):
        global xine
        # create the xine object
        plugin.Plugin.__init__(self)
        try:
            command = config.XINE_COMMAND
        except:
            print '***********************************************************'
            print 'loading xine plugin failed, please set XINE_COMMAND in your'
            print 'local_config.py. Possible good values are'
            print '"xine -V xv -g -f" for using xine while running X'
            print '"fbxine -V vidix"  for using xine on the framebuffer'
            print '***********************************************************'
            return
        
        xine = util.SynchronizedObject(Xine(command))

        # register it as the object to play audio
        plugin.register(xine, plugin.DVD_PLAYER)


class Xine:
    """
    the main class to control xine
    """
    
    def __init__(self, command):
        self.thread = Xine_Thread()
        self.thread.setDaemon(1)
        self.thread.start()
        self.mode = None
        self.app_mode = 'video'
        self.command = command
            
    def play(self, item):
        """
        play a dvd with xine
        """

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.item = item
        self.thread.item = item
        
        if DEBUG:
            print 'Xine.play(): Starting thread, cmd=%s' % command
        rc.app(self)

        skin.get_singleton().clear()
        self.thread.mode    = 'play'
        self.thread.command = '%s dvd://' % self.command
        self.thread.mode_flag.set()
        return None
    

    def stop(self):
        """
        Stop xine and set thread to idle
        """
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        self.thread.item = None
        rc.app(None)
        while self.thread.mode == 'stop':
            time.sleep(0.3)
            

    def eventhandler(self, event):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if event in ( PLAY_END, USER_END ):
            self.stop()
            return self.item.eventhandler(event)

        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)

        

# ======================================================================

class XineApp(childapp.ChildApp):
    """
    class controlling the in and output from the xine process
    """

    def __init__(self, app, item):
        self.item = item
        childapp.ChildApp.__init__(self, app)
        self.exit_type = None
        
    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure Xine shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)


# ======================================================================

class Xine_Thread(threading.Thread):
    """
    Thread to wait for a xine command to play
    """

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None
        self.item  = None

        
    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'play':
                if DEBUG:
                    print 'Xine_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = XineApp(self.command, self.item)

                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                self.app.kill()

                if self.mode == 'play':
                    if self.app.exit_type == "End of file":
                        rc.post_event(PLAY_END)
                    elif self.app.exit_type == "Quit":
                        rc.post_event(USER_END)
                    else:
                        rc.post_event(PLAY_END)
                        
                if DEBUG:
                    print 'Xine_Thread.run(): Stopped'

                self.mode = 'idle'
                skin.get_singleton().redraw()
                
            else:
                self.mode = 'idle'
