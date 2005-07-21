# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# childapp.py - application with a child process
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First edition: Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'Application' ]

# Python imports
import os
import logging

# kaa imports
import kaa.notifier

# Freevo imports
import sysconfig
import config
import gui

from event import *

# application imports
import base

# get logging object
log = logging.getLogger()


class Application(base.Application):
    """
    Basic application controlling one child process.
    """
    def __init__(self, name, eventmap, fullscreen, animated = False,
                 has_display = False):
        """
        Init the application object.
        """
        base.Application.__init__(self, name, eventmap, fullscreen, animated)
        self.__child = None
        self.__stop_cmd = ''
        self.has_display = has_display


    def stop(self):
        """
        Stop the Application.
        """
        if hasattr(self, 'item') and self.has_child():
            self.child_stop()
        else:
            base.Application.stop(self)


    def eventhandler(self, event):
        """
        Simple eventhandler acting on PLAY_END.
        """
        if event == PLAY_END and hasattr(self, 'item') and self.item and \
               event.arg == self.item:
            base.Application.stop(self)
            

    def child_start(self, cmd, prio=0, stop_cmd=''):
        """
        Run the given command as child.
        """
        if self.__child:
            log.error('child already running')
            return False
        if self.fullscreen and self.has_display:
            self.show()
        self.__child = Process(cmd, self, prio, self.has_display)
        self.__stop_cmd = stop_cmd
        return True


    def child_stop(self):
        """
        Stop the child process
        """
        if not self.__child:
            return False
        self.__child.stop(self.__stop_cmd)
        self.__child = None
        return True


    def child_running(self):
        """
        Return True if a child is running right now.
        """
        return self.__child and self.__child.is_alive()


    def has_child(self):
        """
        Return True if the application has a child.
        """
        return self.__child
    

    def child_stdin(self, line):
        """
        Send line to child.
        """
        if self.__child:
            self.__child.write(line)


    def child_stdout(self, line):
        """
        A line from stdout of the child. Override this method to handle
        stdout from the child process.
        """
        pass


    def child_stderr(self, line):
        """
        A line from stdout of the child. Override this method to handle
        stderr from the child process.
        """
        pass


    def child_finished(self):
        """
        Callback when the child is finished. Override this method to react
        when the child is finished.
        """
        self.__child = None
        if hasattr(self, 'item') and self.item:
            PLAY_END.post(self.item)


class Process(kaa.notifier.Process):
    """
    Process wrapping a kaa notifier process into an application.
    Also takes care of basic event sending on start and stop.
    """
    def __init__(self, cmd, handler, prio=0, has_display=False):
        """
        Init the object and start the process.
        """
        self.handler = handler
        self.has_display = has_display
        
        if self.has_display:
            gui.display.hide()
        
        if hasattr(handler, 'item'):
            # send PLAY_START event
            PLAY_START.post(handler.item)

        # get a name for debug logging of the process
        logname = cmd[0]
        if logname.rfind('/') > 0:
            logname = logname[ logname.rfind( '/' ) + 1 : ]
        logname = sysconfig.logfile(logname)

	# start the process
        kaa.notifier.Process.__init__(self, cmd, logname,
                                      callback=self.finished)

        # renice the process
        if prio and config.CONF.renice:
            os.system('%s %s -p %s 2>/dev/null >/dev/null' % \
                      (config.CONF.renice, prio, self.child.pid))


    def stdout_cb(self, line):
        """
        Handle child stdout (send to handler).
        """
        self.handler.child_stdout(line)


    def stderr_cb(self, line):
        """
        Handle child stderr (send to handler).
        """
        self.handler.child_stderr(line)


    def finished(self):
        """
        Callback when child is finished.
        """
        if self.has_display:
            gui.display.show()
        self.handler.child_finished()
