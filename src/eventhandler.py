# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# eventhandler.py - Event handling
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
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

# python imports
import time
import logging

# freevo imports
import sysconfig
import config
import plugin

from event import *

# the logging object
log = logging.getLogger()

GENERIC_HANDLER = 'GENERIC_HANDLER'
EVENT_LISTENER  = 'EVENT_LISTENER'

_singleton = None

def get_singleton():
    """
    get the global application object
    """
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Eventhandler()
        
    return _singleton


def append(application):
    """
    Add app the list of applications and set the focus
    """
    return get_singleton().append(application)


def add_window(window):
    """
    Add a window above all applications (PopupBox)
    """
    return get_singleton().add_window(window)


def remove_window(window):
    """
    Remove window from window list and reset the focus
    """
    return get_singleton().remove_window(window)


def register(application, event):
    """
    Register for a specific event
    """
    return get_singleton().register(application, event)

    
def unregister(application, event):
    """
    Register for a specific event
    """
    return get_singleton().unregister(application, event)

    
def get():
    """
    Return the application which has the focus or the
    PopupBox that is active
    """
    return get_singleton().get()


def is_menu():
    """
    Return true if the focused appliaction is the menu
    """
    return get_singleton().is_menu()


def set_context(context):
    """
    Set context (you should never call this function)
    """
    return get_singleton().set_context(context)


def post(event):
    """
    Send an event to the event queue
    """
    return get_singleton().post(event)
    

# -----------------------------------------------------------------------------

class Eventhandler:
    """
    This is the main application for Freevo, handling applications
    with an event handler and the event mapping.
    """
    def __init__(self):
        self.popups       = []
        self.applications = []
        self.context      = None
        
        self.eventhandler_plugins = None
        self.queue = []
        self.registered = { EVENT_LISTENER : [], GENERIC_HANDLER : []}
        self.stack_change = None
        

    def notify(self, event):
        """
        Notify registered plugins for the given event
        """
        if str(event) in self.registered:
            map(lambda c: c.eventhandler(event), self.registered[str(event)])
                
        
    def set_focus(self):
        """
        change the focus
        """
        if self.stack_change:
            previous, app = self.stack_change
        else:
            previous, app = None, self.applications[-1]
        if not self.popups:
            self.context = app._evt_context
        else:
            self.context = self.popups[-1].event_context

        fade = app._animated
        if previous:
            if previous.visible:
                previous.hide()
            fade = fade or previous._animated
        self.notify(Event(SCREEN_CONTENT_CHANGE,
                          arg=(app, app._evt_fullscreen, fade)))
        self.stack_change = None
        if not app.visible:
            app.show()
        

    def append(self, app):
        """
        Add app the list of applications and set the focus
        """
        # make sure the app is not stopped
        app._evt_stopped = False
        # do will have a stack or is this the first application?
        if len(self.applications) == 0:
            # just add the application
            self.applications.append(app)
            return self.set_focus()
        # check about the old app if it is marked as removed
        # or if it is the same application as before
        previous = self.applications[-1]
        if previous == app:
            previous._evt_stopped = False
        else:
            # hide the application and mark the application change
            previous.hide()
            self.stack_change = previous, app
            if previous._evt_stopped:
                # the previous application is stopped, remove it
                self.applications.remove(previous)
            self.stack_change = previous, app
            self.applications.append(app)
            self.set_focus()


    def add_window(self, window):
        """
        Add a window above all applications (PopupBox)
        """
        self.popups.append(window)
        self.context = window.event_context

        
    def remove_window(self, window):
        """
        Remove window from window list and reset the focus
        """
        if not window in self.popups:
            return
        if not self.popups[-1] == window:
            self.popups.remove(window)
            return
        self.popups.remove(window)
        if self.popups:
            self.context = self.popups[-1].event_context
        else:
            self.context = self.applications[-1]._evt_context
                

    def register(self, application, event):
        """
        Register for a specific event
        """
        event = str(event)
        if not event in self.registered:
            self.registered[event] = []
        if not application in self.registered[event]:
            self.registered[event].append(application)

    
    def unregister(self, application, event):
        """
        Register for a specific event
        """
        self.registered[str(event)].remove(application)

    
    def get(self):
        """
        Return the application
        """
        return self.applications[-1]

    
    def is_menu(self):
        """
        Return true if the focused appliaction is the menu
        """
        return len(self.applications) == 1
    

    def set_context(self, context):
        """
        Set context
        """
        self.context = context

        
    def post(self, event):
        """
        Send an event to the event queue
        """
        if not isinstance(event, Event):
            self.queue += [ Event(event, context=self.context) ]
        else:
            self.queue += [ event ]



    def handle(self, event=None):
        """
        event handling function
        """
        # search for events in the queue
        if not event and not len(self.queue):
            return

        if not event:
            event = self.queue[0]
            del self.queue[0]
        
        log.debug('handling event %s' % str(event))
        
        if config.TIME_DEBUG:
            t1 = time.clock()

        try:
            for p in self.registered[EVENT_LISTENER]:
                p.eventhandler(event=event)

            used = False
            if str(event) in self.registered:
                # event is in the list of registered events. This
                # events are special and should go to the callbacks
                # registered. If at least one of them uses the event
                # (returns True), do not send this event in the event
                # queue (e.g. the detach plugin needs PLAY_END, but
                # will only use it for the audio end and this should
                # not go to the video player)
                for c in self.registered[str(event)]:
                    used = c.eventhandler(event=event) or used

            if event == FUNCTION_CALL:
                # event is a direct function call, call it and do not
                # pass it on the the normal handling
                event.arg()

            elif event.handler:
                # event has it's own handler function, call this
                # function and do not pass it on the the normal
                # handling
                event.handler(event=event)

            elif used:
                # used by registered plugin
                pass
            
            elif len(self.popups) and \
                     self.popups[-1].eventhandler(event=event):
                # handled by the current popup
                pass
                
            elif not self.applications[-1].eventhandler(event=event):
                # pass event to the current application
                for p in self.registered[GENERIC_HANDLER]:
                    # pass it to all plugins when the application
                    # didn't use it
                    if p.eventhandler(event=event):
                        break
                else:
                    # nothing found for this event
                    log.debug( 'no eventhandler for event %s (app: %s)' \
                               % (event, self.applications[-1]))

            # now do some checking if the focus needs to be changed
            if self.stack_change:
                # our stack has changed, reset the focus
                self.set_focus()
            elif self.applications[-1]._evt_stopped or \
                     not self.applications[-1].visible:
                # the current application wants to be removed, either
                # because stop() is called or the hide() function was
                # called from the event handling
                previous, current = self.applications[-2:]
                self.applications.remove(current)
                self.stack_change = current, previous
                self.set_focus()

            if config.TIME_DEBUG:
                print time.clock() - t1
            return True

        except SystemExit:
            raise SystemExit

        except:
            if config.FREEVO_EVENTHANDLER_SANDBOX:

                import gui
                import cleanup

                log.exception('eventhandler')
                msg=_('Event \'%s\' crashed\n\nPlease take a ' \
                      'look at the logfile and report the bug to ' \
                      'the Freevo mailing list. The state of '\
                      'Freevo may be corrupt now and this error '\
                      'could cause more errors until you restart '\
                      'Freevo.\n\nLogfile: %s') % \
                      (event, sysconfig.syslogfile)

                pop = gui.ConfirmBox(msg, handler=cleanup.shutdown,
                                     handler_message = _('shutting down...'),
                                     button0_text = _('Shutdown'),
                                     button1_text = _('Continue')).show()
            else:
                raise 
