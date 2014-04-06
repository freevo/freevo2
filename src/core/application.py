# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# base.py - Basic Application
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2009 Dirk Meyer, et al.
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

__all__ = [ 'Application', 'STATUS_RUNNING', 'STATUS_STOPPING', 'STATUS_STOPPED',
            'STATUS_IDLE', 'CAPABILITY_TOGGLE', 'CAPABILITY_PAUSE',
            'CAPABILITY_FULLSCREEN' ]

# python imports
import logging

# kaa imports
import kaa

# freevo imports
from .. import gui
import api as freevo

# application imports
from taskmanager import taskmanager

# get logging object
log = logging.getLogger()

STATUS_IDLE     = 'idle'
STATUS_RUNNING  = 'running'
STATUS_STOPPING = 'stopping'
STATUS_STOPPED  = 'stopped'

CAPABILITY_TOGGLE     = 1
CAPABILITY_PAUSE      = 2
CAPABILITY_FULLSCREEN = 4

class WidgetContext(object):
    """
    Context link between Application and view
    """

    _instances = []
    _changed = False

    def __init__(self, name):
        self._ctx = kaa.candy.Context()
        self._name = name
        self._widget = None
        WidgetContext._instances.append(kaa.weakref.weakref(self))

    def create_widget(self, fullscreen):
        """
        Render the widget
        """
        self._widget = gui.show_application(self._widget or self._name, fullscreen, self._ctx)

    def remove_widget(self):
        """
        Remove the widget
        """
        if self._widget:
            self._widget = gui.destroy_application(self._widget)

    @classmethod
    def sync(cls, force=True):
        """
        Update all widgets
        """
        if not (WidgetContext._changed or force):
            return
        WidgetContext._changed = False
        for obj in WidgetContext._instances[:]:
            if not obj:
                WidgetContext._instances.remove(obj)
            elif obj._widget:
                obj._widget.context = obj._ctx

    def __getattr__(self, attr):
        """
        Get context attribute
        """
        return self._ctx.get(attr)

    def __setattr__(self, attr, value):
        """
        Set context attribute
        """
        if attr.startswith('_') or attr == 'widget':
            return super(WidgetContext, self).__setattr__(attr, value)
        WidgetContext._changed = True
        self._ctx[attr] = value

# Ugly monkey patch to make sure sync is called after everything else
# is done and before we enter the mainloop again and may sleep.
notifier_step = kaa.main.notifier.step
def step():
    WidgetContext.sync(force=False)
    notifier_step()
kaa.main.notifier.step = step


class Application(freevo.ResourceHandler):
    """
    A basic application
    """

    # variables to override
    name = None

    def __init__(self, eventmap, capabilities=[]):
        """
        Init the Application object.
        """
        self.signals = kaa.Signals('show', 'hide', 'start', 'stop')
        self.__status = STATUS_IDLE
        self.__eventmap = eventmap
        self.__capabilities = 0
        self.context = WidgetContext(self.name)
        for cap in capabilities:
            self.__capabilities |= cap

    @property
    def widget(self):
        """
        Return the GUI widget if created or None
        """
        return self.context._widget

    def has_capability(self, capability):
        """
        Return True if the application has the given capability.
        """
        return (self.__capabilities & capability) != 0

    def reset(self):
        """
        Reset application due to kaa.candy failure
        """
        self.status = STATUS_IDLE

    @property
    def status(self):
        """
        Return the current application status.
        """
        return self.__status

    @status.setter
    def status(self, status):
        """
        Set application status and react on some changes.
        """
        if status in (STATUS_STOPPED, STATUS_IDLE):
            self.free_resources()
        if status == STATUS_RUNNING and self.__status == STATUS_IDLE:
            taskmanager.show_application(self)
            self.__status = status
            self.signals['start'].emit()
        elif status == STATUS_IDLE:
            taskmanager.hide_application(self)
            self.free_resources(resume=True)
            self.__status = status
            self.signals['stop'].emit()
        else:
            self.__status = status

    @property
    def eventmap(self):
        """
        Return the eventmap for the application.
        """
        return self.__eventmap

    @eventmap.setter
    def eventmap(self, eventmap):
        """
        Set a new eventmap for the event handler
        """
        self.__eventmap = eventmap
        taskmanager.sync()

    def eventhandler(self, event):
        """
        Eventhandler for this application
        """
        raise RuntimeError('no eventhandler defined for %s' % self.name)

    def stop(self):
        """
        Stop the application. If it is not shown again in the same cycle, the
        hide() function will be called. If the app isn't really stopped now
        (e.g. a child needs to be stopped), do not call this function.
        """
        self.__status = STATUS_STOPPED

    def get_json(self, httpserver):
        """
        Return a dict with attributes about the application used by
        the provided httpserver to send to a remote controlling
        client.
        """
        return {}

    def __repr__(self):
        """
        String for debugging.
        """
        return '<Freevo.Application %s>' % self.name
