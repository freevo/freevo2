# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# eventhandler.py - Event handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/08/01 10:53:54  dischi
# o Add class for an Application. This class works together with the
#   eventhandler itself and can show/hide/destry itself.
# o Respect the difference between a popup and an application in the
#   eventhandler focus setting
# o Make it possible to switch screen backends for an application
# o Make it possible to register to an event
# o Notify registered eventhandlers for application change
#
# Revision 1.1  2004/07/26 18:10:16  dischi
# move global event handling to eventhandler.py
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


import time
import thread
import traceback

import config
import gui

from event import *


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


def remove(application):
    """
    Remove app the list of applications and set the focus
    """
    return get_singleton().remove(application)


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
    Return the application which has the focus
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
    

def post_key(key):
    """
    Send a keyboard event to the event queue
    """
    return get_singleton().post_key(key)




# --------------------------------------------------------------------------------

class Application:
    """
    A basic application
    """
    def __init__(self, name, event_context, fullscreen, backend='default'):
        self.evt_name       = name
        self.evt_context    = event_context
        self.evt_fullscreen = fullscreen
        self.evt_handler    = get_singleton()
        self.evt_backend    = backend
        self.post_event     = self.evt_handler.post
        self.visible        = False
        
    def eventhandler(self, event, menuw=None):
        print 'Error, no eventhandler defined for %s' % self.application


    def show(self):
        self.visible = True
        self.evt_handler.append(self)
        if traceback.extract_stack(limit = 2)[0][3] != 'Application.show(self)':
            gui.get_screen().update()
            
        
    def hide(self):
        if self.evt_handler.applications[-1] == self:
            _debug_('WARNING: hiding focused application')
            self.evt_handler.remove(self)
        self.visible = False


    def destroy(self):
        self.evt_handler.remove(self)
        self.visible = False
        

APPEND = 'append'
REMOVE = 'remove'

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
        self.registered = {}
        self.focus_change = None
        self.backend = 'default'
        

    def set_focus(self):
        app = self.applications[-1]
        if not self.popups:
            self.context = app.evt_context
        else:
            self.context = self.popups[-1].evt_context
            
        if str(SCREEN_CONTENT_CHANGE) in self.registered:
            for c in self.registered[str(SCREEN_CONTENT_CHANGE)]:
                arg = app, app.evt_fullscreen
                c.eventhandler(Event(SCREEN_CONTENT_CHANGE, arg=arg))
        if self.backend != 'default' or app.evt_backend != 'default':
            _debug_('**** backend switch: %s ****' % app.evt_backend)
            gui.set_screen(app.evt_backend)
            self.backend = app.evt_backend
        if self.focus_change == REMOVE:
            _debug_('show hidden application')
            app.show()
        self.focus_change = None
        

    def append(self, app):
        """
        Add app the list of applications and set the focus
        """
        if isinstance(app, Application):
            if app in self.applications:
                return

            self.applications.append(app)
            if len(self.applications) > 1:
                self.applications[-2].hide()
            self.context = app.evt_context
            self.set_focus()
        else:
            self.popups.append(app)
            self.context = app.evt_context


    def remove(self, app):
        """
        Remove app the list of applications and set the focus
        """
        if isinstance(app, Application):
            if not app in self.applications:
                return
            if self.applications[-1] == app:
                self.focus_change = REMOVE
            self.applications.remove(app)
                
        else:
            if not app in self.popups:
                return
            if not self.popups[-1] == app:
                self.popups.remove(app)
                return
            self.popups.remove(app)
            if self.popups:
                self.context = self.popups[-1].evt_context
            else:
                self.context = self.applications[-1].evt_context
                

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
        Return the application which has the focus
        """
        if len(self.popups):
            return self.popups[-1]
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



    def post_key(self, key):
        """
        Send a keyboard event to the event queue
        """
        if not key:
            return None

        for c in (self.context, 'global'):
            try:
                e = config.EVENTS[c][key]
                e.context = self.context
                self.queue.append(e)
                break
            except KeyError:
                pass
        else:
            if self.context != 'input':
                print 'no event mapping for key %s in context %s' % (key, self.context)
                print 'send button event BUTTON arg=%s' % key
            self.queue.append(Event(BUTTON, arg=key))



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
        
        _debug_('handling event %s' % str(event), 2)

        if self.eventhandler_plugins == None:
            import plugin
            _debug_('init', 1)
            self.eventhandler_plugins  = []
            self.eventlistener_plugins = []

            for p in plugin.get('daemon_eventhandler'):
                if hasattr(p, 'event_listener') and p.event_listener:
                    self.eventlistener_plugins.append(p)
                else:
                    self.eventhandler_plugins.append(p)
            
        for p in self.eventlistener_plugins:
            p.eventhandler(event=event)

        if event == FUNCTION_CALL:
            return event.arg()

        if event.handler:
            return event.handler(event=event)

        if config.TIME_DEBUG:
            t1 = time.clock()

        try:
            if str(event) in self.registered:
                for c in self.registered[str(event)]:
                    c.eventhandler(event=event)

            elif len(self.popups) and self.popups[-1].eventhandler(event=event):
                pass
                
            elif not self.applications[-1].eventhandler(event=event):
                for p in self.eventhandler_plugins:
                    if p.eventhandler(event=event):
                        break
                else:
                    _debug_('no eventhandler for event %s (app: %s)' \
                            % (event, self.applications[-1]), 2)

            if self.focus_change:
                self.set_focus()
                
            if config.TIME_DEBUG:
                print time.clock() - t1
            return True

        except SystemExit:
            raise SystemExit

        except:
            if config.FREEVO_EVENTHANDLER_SANDBOX:
                import traceback
                import gui
                from plugins.shutdown import shutdown

                traceback.print_exc()
                pop = gui.ConfirmBox(text=_('Event \'%s\' crashed\n\nPlease take a ' \
                                            'look at the logfile and report the bug to ' \
                                            'the Freevo mailing list. The state of '\
                                            'Freevo may be corrupt now and this error '\
                                            'could cause more errors until you restart '\
                                            'Freevo.\n\nLogfile: %s\n\n') % \
                                     (event, sys.stdout.logfile),
                                     width=osd.width-2*config.OSD_OVERSCAN_X-50,
                                     handler=shutdown,
                                     handler_message = _('shutting down...'))
                pop.b0.set_text(_('Shutdown'))
                pop.b0.toggle_selected()
                pop.b1.set_text(_('Continue'))
                pop.b1.toggle_selected()
                pop.show()
            else:
                raise 
