#if 0 /*
# -----------------------------------------------------------------------
# xine.py - the Freevo XINE module for audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes: Use xine (or better fbxine) to play audio files. This requires
#        xine-ui > 0.9.22 (when writing this plugin this means cvs)
#
# Todo:  test it
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/08/26 20:24:07  outlyer
# Apparently some files have spaces in them... D'oh :)
#
# Revision 1.2  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
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
import popen2, re

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import rc         # The RemoteControl class.

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
    Xine plugin for the video player.
    """
    def __init__(self):
        global xine

        plugin.Plugin.__init__(self)

        if xine:
            return

        try:
            config.CONF.fbxine
        except:
            print '\nERROR:\nfbxine not found, plugin deactivated'
            return

        xine_version = 0
        xine_cvs     = 0
        
        child = popen2.Popen3('%s --version' % config.CONF.fbxine, 1, 100)
        while(1):
            data = child.fromchild.readline()
            if not data:
                break
            m = re.match('^.* v?([0-9])\.([0-9]+)\.([0-9]*).*', data)
            if m:
                if data.find('cvs') >= 0:
                    xine_cvs = 1
                xine_version =int('%02d%02d%02d' % (int(m.group(1)), int(m.group(2)),
                                                    int(m.group(3))))

        child.wait()

        if xine_cvs:
            xine_version += 1
            
        if xine_version < 923:
            print '\nERROR:\nfbxine version to old, plugin deactivated'
            print 'You need xine-ui > 0.9.22\n'
            return
            
        # create the xine object
        xine = util.SynchronizedObject(Xine(xine_version))

        # register it as the object to play
        plugin.register(xine, plugin.AUDIO_PLAYER)


class Xine:
    """
    the main class to control xine
    """
    
    def __init__(self, version):
        self.thread = Xine_Thread()
        self.thread.setDaemon(1)
        self.thread.start()
        self.mode = None
        self.xine_version = version
        self.app_mode = 'audio'

        self.command = '%s -V none -A %s --stdctl' % (config.CONF.fbxine, config.XINE_AO_DEV)
        if rc.PYLIRC:
            self.command = '%s --no-lirc' % self.command

        
    def play(self, item, playerGUI):
        """
        play an audio file with xine
        """

        if item.url:
            filename = item.url
        else:
            filename = item.filename

        self.playerGUI = playerGUI
        
        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.item = item
        self.thread.item = item
        
        command = self.command
        
        if DEBUG:
            print 'Xine.play(): Starting thread, cmd=%s' % command

        self.thread.mode    = 'play'
        self.thread.command = '%s "%s"' % (command, filename)
        self.thread.mode_flag.set()
        return None
    

    def is_playing(self):
        return self.thread.mode != 'idle'


    def refresh(self):
        self.playerGUI.refresh()
        

    def stop(self):
        """
        Stop xine and set thread to idle
        """
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        self.thread.item = None
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

        if event == PAUSE or event == PLAY:
            self.thread.app.write('pause\n')
            return TRUE

        if event == STOP:
            self.thread.app.write('quit\n')
            for i in range(10):
                if self.thread.mode == 'idle':
                    break
                time.sleep(0.3)
            else:
                # sometimes xine refuses to die
                self.stop()
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        if event == SEEK:
            pos = int(event.arg)
            if pos < 0:
                action='SeekRelative-'
                pos = 0 - pos
            else:
                action='SeekRelative+'
            if pos <= 15:
                pos = 15
            elif pos <= 30:
                pos = 30
            else:
                pos = 30
            self.thread.app.write('%s%s\n' % (action, pos))
            return TRUE

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
        self.elapsed = 0


    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure Xine shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)


    def stdout_cb(self, line):
        if line.startswith("time: "):         # get current time
            self.item.elapsed = int(line[6:])

            if self.item.elapsed != self.elapsed:
                xine.refresh()
            self.elapsed = self.item.elapsed


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
                
            else:
                self.mode = 'idle'
