# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# application.py - Event and Application handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
#
# Todo:        move event mapping from rc.py in this file
#              (see the FIXME comments for bad rc.py updates)
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/25 19:46:33  dischi
# new class for application / focus / event handling
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

import config
from event import *


_singleton = None

def get_singleton():
    """
    get the global application object
    """
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Application()
        
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




class Application:
    """
    This is the main application for Freevo, handling applications
    with an event handler and the event mapping.
    """
    def __init__(self):
        self.focus   = []
        self.context = None

        self.eventhandler_plugins = None


    def append(self, app):
        """
        Add app the list of applications and set the focus
        """
        if app in self.focus:
            return
        if hasattr(app, 'app_mode'):
            self.context = app.app_mode
        else:
            self.context = app.event_context
        self.focus.append(app)
        # FIXME:
        import rc
        rc.get_singleton().context = self.context


    def remove(self, app):
        """
        Remove app the list of applications and set the focus
        """
        try:
            self.focus.remove(app)
        except Exception, e:
            print e
        app = self.focus[-1]
        if hasattr(app, 'app_mode'):
            self.context = app.app_mode
        else:
            self.context = app.event_context
        # FIXME:
        import rc
        rc.get_singleton().context = self.context


    def get(self):
        """
        Return the application which has the focus
        """
        return self.focus[-1]

    
    def is_menu(self):
        """
        Return true if the focused appliaction is the menu
        """
        return len(self.focus) == 1
    

    def set_context(self, context):
        """
        Set context
        """
        self.context = context
        # FIXME:
        import rc
        rc.get_singleton().context = self.context

        
    def eventhandler(self, event):
        """
        event handling function
        """
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
            if not self.focus[-1].eventhandler(event=event):
                for p in self.eventhandler_plugins:
                    if p.eventhandler(event=event):
                        break
                else:
                    _debug_('no eventhandler for event %s (app: %s)' \
                            % (event, self.focus[-1]), 2)

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



    def run(self):
        """
        Run the main loop (FIXME: should only be a callback)
        """
        import rc
        while 1:
            get_singleton().eventhandler(rc.get_event(True))

        
