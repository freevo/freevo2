#if 0 /*
# -----------------------------------------------------------------------
# rc.py - Remote control / Event and Callback handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This is the only class to be thread safe!
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.35  2004/05/31 10:39:55  dischi
# Again some interface changes. There is now only one function
# handling all callbacks, including repeating calls with timer
#
# Revision 1.34  2004/05/30 18:27:53  dischi
# More event / main loop cleanup. rc.py has a changed interface now
#
# Revision 1.33  2004/05/29 19:06:26  dischi
# move some code from main to rc, create main class
#
# Revision 1.32  2004/05/20 18:26:27  dischi
# patch from Viggo
#
# Revision 1.31  2004/05/09 14:16:16  dischi
# let the child stdout handled by main
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

import os
import copy
import time
import thread
import types

import config

from event import Event, BUTTON

SHUTDOWN = -1

PYLIRC     = False
_singleton = None


def get_singleton(**kwargs):
    """
    get the global rc object
    """
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = EventHandler(**kwargs)
        
    return _singleton


def post_event(event):
    """
    add an event to the event queue
    """
    return get_singleton().post_event(event)


def app(application=0):
    """
    set or get the current app/eventhandler
    """
    if not application == 0:
        context = 'menu'
        if hasattr(application, 'app_mode'):
            context = application.app_mode
        if hasattr(application, 'eventhandler'):
            application = application.eventhandler
        get_singleton().set_app(application, context)

    return get_singleton().get_app()


def set_context(context):
    """
    set the context (map with button->event transformation
    """
    return get_singleton().set_context(context)


def register(function, repeat, timer, *arg):
    """
    register an function to be called
    repeat: if true, call the function later again
    timer:  timer * 0.01 seconds when to call the function
    """
    return get_singleton().register(function, repeat, timer, *arg)


def unregister(object):
    """
    unregister an object from the main loop
    """
    return get_singleton().unregister(object)


def shutdown():
    """
    shutdown the rc
    """
    return get_singleton().shutdown()


def poll():
    """
    poll all registered callbacks
    """
    return get_singleton().poll()


def get_event(blocking=False):
    """
    get next event. If blocking is True, this function will block until
    there is a new event (also call all registered callbacks while waiting)
    """
    return get_singleton().get_event(blocking)


# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# internal classes of this module
# --------------------------------------------------------------------------------

class Lirc:
    """
    Class to handle lirc events
    """
    def __init__(self):
        try:
            import pylirc
        except ImportError:
            print 'WARNING: PyLirc not found, lirc remote control disabled!'
            raise Exception
        try:
            if os.path.isfile(config.LIRCRC):
                pylirc.init('freevo', config.LIRCRC)
                pylirc.blocking(0)
            else:
                raise IOError
        except RuntimeError:
            print 'WARNING: Could not initialize PyLirc!'
            raise Exception
        except IOError:
            print 'WARNING: %s not found!' % config.LIRCRC
            raise Exception

        self.nextcode = pylirc.nextcode

        self.previous_returned_code   = None
        self.previous_code            = None;
        self.repeat_count             = 0
        self.firstkeystroke           = 0.0
        self.lastkeystroke            = 0.0
        self.lastkeycode              = ''
        self.default_keystroke_delay1 = 0.25  # Config
        self.default_keystroke_delay2 = 0.25  # Config

        global PYLIRC
        PYLIRC = True

        
    def get_last_code(self):
        """
        read the lirc interface
        """
        result = None

        if self.previous_code != None:
            # Let's empty the buffer and return the most recent code
            while 1:
                list = self.nextcode();
                if list != []:
                    break
        else:
            list = self.nextcode()

        if list == []:
            # It's a repeat, the flag is 0
            list   = self.previous_returned_code
            result = list

        elif list != None:
            # It's a new code (i.e. IR key was released), the flag is 1
            self.previous_returned_code = list
            result = list

        self.previous_code = result
        return result



    def poll(self, rc):
        """
        return next event
        """
        list = self.get_last_code()

        if list == None:
            nowtime = 0.0
            nowtime = time.time()
            if (self.lastkeystroke + self.default_keystroke_delay2 < nowtime) and \
                   (self.firstkeystroke != 0.0):
                self.firstkeystroke = 0.0
                self.lastkeystroke = 0.0
                self.repeat_count = 0

        if list != None:
            nowtime = time.time()

            if list:
                for code in list:
                    if ( self.lastkeycode != code ):
                        self.lastkeycode = code
                        self.lastkeystroke = nowtime
                        self.firstkeystoke = nowtime

            if self.firstkeystroke == 0.0 :
                self.firstkeystroke = time.time()
            else:
                if (self.firstkeystroke + self.default_keystroke_delay1 > nowtime):
                    list = []
                else:
                    if (self.lastkeystroke + self.default_keystroke_delay2 < nowtime):
                        self.firstkeystroke = nowtime

            self.lastkeystroke = nowtime
            self.repeat_count += 1

            for code in list:
                return code

        
# --------------------------------------------------------------------------------

class Keyboard:
    """
    Class to handle keyboard input
    """
    def __init__(self):
        """
        init the keyboard event handler
        """
        import osd
        self.callback = osd.get_singleton()._cb


    def poll(self, rc):
        """
        return next event
        """
        return self.callback(rc.context != 'input')


# --------------------------------------------------------------------------------

class Network:
    """
    Class to handle network control
    """
    def __init__(self):
        """
        init the network event handler
        """
        import socket
        self.port = config.REMOTE_CONTROL_PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind(('', self.port))
        

    def poll(self, rc):
        """
        return next event
        """
        try:
            return self.sock.recv(100)
        except:
            # No data available
            return None


# --------------------------------------------------------------------------------
    
class EventHandler:
    """
    Class to transform input keys or buttons into events. This class
    also handles the complete event queue (post_event)
    """
    def __init__(self, use_pylirc=1, use_netremote=1):

        self.inputs = []
        if use_pylirc:
            try:
                self.inputs.append(Lirc())
            except:
                pass

        try:
            self.inputs.append(Keyboard())
        except:
            pass

        if use_netremote and config.ENABLE_NETWORK_REMOTE and \
               config.REMOTE_CONTROL_PORT:
            self.inputs.append(Network())

        self.app                = None
        self.context            = 'menu'
        self.queue              = []
        self.event_callback     = None
        self.callbacks          = []
        self.shutdown_callbacks = []
        self.poll_objects       = []
        # lock all critical parts
        self.lock               = thread.allocate_lock()
        # last time we stopped sleeping
        self.sleep_timer        = 0
        

    def set_app(self, app, context):
        """
        set default eventhandler and context
        """
        self.app     = app
        self.context = context


    def get_app(self):
        """
        get current eventhandler (app)
        """
        return self.app


    def set_context(self, context):
        """
        set context for key mapping
        """
        self.context = context
        

    def post_event(self, e):
        """
        add event to the queue
        """
        self.lock.acquire()
        if not isinstance(e, Event):
            self.queue += [ Event(e, context=self.context) ]
        else:
            self.queue += [ e ]
        self.lock.release()

        if self.event_callback:
            self.event_callback()


    def key_event_mapper(self, key):
        """
        map key to event based on current context
        """
        if not key:
            return None

        for c in (self.context, 'global'):
            try:
                e = config.EVENTS[c][key]
                e.context = self.context
                return e
            except KeyError:
                pass

        if self.context != 'input':
            print 'no event mapping for key %s in context %s' % (key, self.context)
            print 'send button event BUTTON arg=%s' % key
        return Event(BUTTON, arg=key)


    def register(self, function, repeat, timer, *arg):
        """
        register an function to be called
        repeat: if true, call the function later again
        timer:  timer * 0.01 seconds when to call the function
        """
        self.lock.acquire()
        if timer == SHUTDOWN:
            _debug_('register shutdown callback: %s' % function, 2)
            self.shutdown_callbacks.append([ function, arg ])
        else:
            if repeat:
                _debug_('register callback: %s' % function, 2)
            self.callbacks.append([ function, repeat, timer, 0, arg ])
        self.lock.release()

        
    def unregister(self, function):
        """
        unregister an object from the main loop
        """
        self.lock.acquire()
        for c in copy.copy(self.callbacks):
            if c[0] == function:
                _debug_('unregister callback: %s' % function, 2)
                self.callbacks.remove(c)
        for c in copy.copy(self.shutdown_callbacks):
            if c[0] == function:
                _debug_('unregister shutdown callback: %s' % function, 2)
                self.shutdown_callbacks.remove(c)
        self.lock.release()

        
    def shutdown(self):
        """
        shutdown the rc
        """
        for c in copy.copy(self.shutdown_callbacks):
            _debug_('shutting down %s' % c[0], 2)
            c[0](*c[1])


    def poll(self):
        """
        poll all registered functions
        """
        # run all registered callbacks
        for c in copy.copy(self.callbacks):
            if c[2] == c[3]:
                # time is up, call it:
                c[0](*c[4])
                if not c[1]:
                    # remove if it is no repeat callback:
                    self.lock.acquire()
                    self.callbacks.remove(c)
                    self.lock.release()
                else:
                    # reset counter for next run
                    c[3] = 0
            else:
                c[3] += 1


    def get_event(self, blocking=False):
        """
        get next event. If blocking is True, this function will block until
        there is a new event (also call all registered callbacks while waiting)
        """
        if blocking:
            while 1:
                # get non blocking event
                event = self.get_event(False)
                if event:
                    return event
                # poll everything
                self.poll()

                # wait some time
                duration = 0.01 - (time.time() - self.sleep_timer)
                if duration > 0:
                    time.sleep(duration)
                self.sleep_timer = time.time()

                
        # search for events in the queue
        if len(self.queue):
            self.lock.acquire()
            ret = self.queue[0]
            del self.queue[0]
            self.lock.release()
            return ret

        # search all input objects for new events
        for i in self.inputs:
            e = i.poll(self)
            if e:
                return self.key_event_mapper(e)

        return None



    def subscribe(self, event_callback=None):
        """
        subscribe to 'post_event'
        """
        if not event_callback:
            return

        self.event_callback = event_callback
