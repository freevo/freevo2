# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# childapp.py - runs an application in a child process
# -----------------------------------------------------------------------------
# $Id$
#
# Run a child application inside Freevo. This file will be removed. Please
# use application.ChildApp.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First edition: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------


__all__ = [ 'Instance' ]

# Python imports
import os

# kaa imports
import kaa.notifier

# Freevo imports
import sysconfig
import config
import gui

from event import *

class Instance(kaa.notifier.Process):
    def __init__( self, app, debugname = None, doeslogging = 0, prio = 0,
                  stop_osd = 2 ):
        self.is_video = 0
        if stop_osd == 2: 
            self.is_video = 1
            VIDEO_START.post()
            stop_osd = 1

        self.stop_osd = stop_osd
        if self.stop_osd:
            gui.display.hide()
        
        if hasattr(self, 'item'):
            PLAY_START.post(self.item)

        if isinstance( app, unicode ):
            app = String(app)
            
        if not debugname:
            if isinstance(app, str):
                debugname = app[ : app.find( ' ' ) ]
            else:
                debugname = app[ 0 ]

            if debugname.rfind('/') > 0:
                debugname = debugname[ debugname.rfind( '/' ) + 1 : ]

        if debugname:
	    debugname = sysconfig.logfile(debugname)
	
        kaa.notifier.Process.__init__(self, app, debugname)
 
        self.signals["stdout"].connect(self.stdout_cb)
        self.signals["stderr"].connect(self.stderr_cb)
        self.signals["completed"].connect(self.finished)

        kaa.notifier.Process.start(self)
        
        if prio and config.CONF.renice:
            os.system('%s %s -p %s 2>/dev/null >/dev/null' % \
                      (config.CONF.renice, prio, self.child.pid))


    def stop(self, cmd = ''):
        """
        Stop child and wait.
        """
        kaa.notifier.Process.stop(self, cmd)
        while self.is_alive():
            kaa.notifier.step()
        

    def stop_event(self):
        """
        Event to send on stop
        """
        return PLAY_END


    def stdout_cb(self, line):
        """
        Handle stdout of the process.
        """
        pass


    def stderr_cb(self, line):
        """
        Handle stderr of the process.
        """
        pass
        

    def finished(self, exit_code):
        # Ok, we can use the OSD again.
        if self.stop_osd:
            gui.display.show()

        if not self.stopping:
            if self.is_video:
                VIDEO_END.post()
            self.stop_event().post()

        
