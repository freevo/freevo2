# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# taskmanager.py - Handle active applications and windows
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines the taskmanager. It will manage the current active
# applications and windows, show/hide them and send events to the
# application or window with the focus.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2013 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

__all__ = [ 'taskmanager', 'signals' ]

# python imports
import logging

# kaa imports
import kaa

# freevo imports
import api as freevo
from .. import gui

# the logging object
log = logging.getLogger()

# the global object
taskmanager = None

STATUS_IDLE     = 'idle'
STATUS_RUNNING  = 'running'
STATUS_STOPPING = 'stopping'
STATUS_STOPPED  = 'stopped'

CAPABILITY_TOGGLE = 1

class AliveMonitor(object):
    """
    Monitor the taskmanager for blocking tasks and fade out the GUI if
    this happens.
    """
    def __init__(self):
        self.timer = kaa.OneShotTimer(gui.set_active, False)

    def __call__(self, inprogress, secs):
        self.timer.start(secs)
        inprogress.connect(self.__stop)

    def __stop(self, *args):
        self.timer.stop()
        if not gui.active:
            gui.set_active(True)

# global object
monitor = AliveMonitor()


class TaskManager(kaa.Object):
    """
    This is the main application for Freevo, handling applications
    with an event handler and the event mapping.
    """

    __kaasignals__ = {
        'application-change':
            '''
            Emitted when the current application changes
            '''
    }

    def __init__(self):
        super(TaskManager, self).__init__()
        self.applications = []
        self.current = None
        self.windows = []
        self.eventmap = None
        kaa.EventHandler(self.eventhandler).register()
        gui.signals['reset'].connect(self.reset)

    def reset(self):
        """
        GUI reset
        """
        log.warning('kaa.candy reset, going back to menu')
        while len(self.applications) > 1:
            app = self.applications.pop()
            app.reset()
            app.context.remove_widget()
        self.current = None
        self.sync()
        
    def sync(self):
        """
        Set new focus (input mapping, application show/hide)
        """
        app = self.applications[-1]
        # set input mapping
        focus = app
        if self.windows:
            focus = self.windows[-1]
        if self.eventmap != focus.eventmap:
            log.info('set focus to %s' % focus)
            self.eventmap = focus.eventmap
        if app == self.current:
            # same app as before
            return
        log.info('switch application from %s to %s' % (self.current, app))
        self.signals['application-change'].emit(app)
        app.signals['show'].emit()
        app.context.create_widget(app.has_capability(freevo.CAPABILITY_FULLSCREEN))
        if self.current:
            self.current.signals['hide'].emit()
        self.current = app

    def show_application(self, app):
        """
        Show application and set the focus
        """
        log.info('show application %s' % app)
        # do will have a stack or is this the first application?
        if len(self.applications) == 0:
            # just add the application
            self.applications.append(app)
            self.sync()
            return True
        # check about the old app if it is marked as removed
        # or if it is the same application as before
        previous = self.applications[-1]
        if previous == app:
            # It is the same app, nothing to do
            return True
        if app in self.applications:
            # already in list, remove it before appending
            self.applications.remove(app)
        # check if an application is in status stopped and replace it.
        for pos, a in enumerate(self.applications):
            if a.status == STATUS_STOPPED:
                self.applications[pos] = app
                break
        else:
            # no stopped application, just append to the list
            self.applications.append(app)
        self.sync()

    def hide_application(self, app):
        """
        Remove application from stack.
        """
        log.info('hide application %s' % app)
        app.context.remove_widget()
        if not app in self.applications:
            # already gone (maybe by show_application of a new one)
            return
        if not app == self.applications[-1]:
            # not visible, just remove
            self.applications.remove(app)
            return
        # remove from list and set new focus
        self.applications.pop()
        self.sync()

    def add_window(self, window):
        """
        Add a window above all applications
        """
        self.windows.append(window)
        self.sync()

    def remove_window(self, window):
        """
        Remove window from window list and reset the focus
        """
        if not window in self.windows:
            return
        self.windows.remove(window)
        self.sync()

    def eventhandler(self, event):
        """
        Event handling function.
        """
        log.debug('handling event %s' % str(event))
        if event == freevo.TOGGLE_APPLICATION and len(self.applications) > 1 and \
               self.applications[-1].has_capability(CAPABILITY_TOGGLE):
            log.info('Toggle application')
            self.applications.insert(0, self.applications.pop())
            self.sync()
            return True
        result = None
        if event.handler:
            # event has it's own handler function, call this
            # function and do not pass it on the the normal
            # handling.
            result = event.handler(event=event) or True
            if event.handler == self.applications[-1].eventhandler:
                # handler is the current visible application, also
                # pass to the GUI code just as without the special
                # handler.
                self.applications[-1].widget.eventhandler(event)
        if not result and len(self.windows):
            # maybe handled by the current popup
            result = self.windows[-1].eventhandler(event=event)
        if not result:
            # handle by the current application
            result = self.applications[-1].eventhandler(event=event)
            self.applications[-1].widget.eventhandler(event)
        if isinstance(result, kaa.InProgress) and not (len(self.windows) and self.windows[-1].busy):
            monitor(result, 0.5)
        return result


# create the global object
taskmanager = TaskManager()

# expose signals
signals = taskmanager.signals
