#if 0 /*
# -----------------------------------------------------------------------
# rc.py - Remote control / Event and Callback handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.33  2004/05/29 19:06:26  dischi
# move some code from main to rc, create main class
#
# Revision 1.32  2004/05/20 18:26:27  dischi
# patch from Viggo
#
# Revision 1.31  2004/05/09 14:16:16  dischi
# let the child stdout handled by main
#
# Revision 1.30  2004/02/28 17:30:59  dischi
# fix crash for helper
#
# Revision 1.29  2004/02/27 20:12:16  dischi
# reworked rc.py to make several classes
#
# Revision 1.28  2003/12/14 17:24:59  dischi
# cleanup
#
# Revision 1.27  2003/11/02 10:50:15  dischi
# better error handling
#
# Revision 1.26  2003/10/26 17:04:26  dischi
# Patch from Soenke Schwardt to use the time to fix repeat problems with
# some remote receiver.
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

import config
import util
from event import Event, BUTTON

PYLIRC     = False
_singleton = None

def get_singleton(**kwargs):
    """
    get the global rc object
    """
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = util.SynchronizedObject(RemoteControl(**kwargs))
        
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
    get_singleton().set_context(context)


def callback(function, *arg):
    get_singleton().one_time_callbacks.append((function, arg))


def register(object):
    """
    register an object to the main loop
    """
    get_singleton().register(object)


def unregister(object):
    """
    unregister an object from the main loop
    """
    get_singleton().unregister(object)


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
    
class RemoteControl:
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

        self.app                      = None
        self.context                  = 'menu'
        self.queue                    = []
        self.event_callback           = None
        self.one_time_callbacks       = []
        self.poll_objects             = []

    def set_app(self, app, context):
        self.app     = app
        self.context = context


    def get_app(self):
        return self.app


    def set_context(self, context):
        self.context = context
        

    def post_event(self, e):
        if not isinstance(e, Event):
            self.queue += [ Event(e, context=self.context) ]
        else:
            self.queue += [ e ]

        if self.event_callback:
            self.event_callback()


    def key_event_mapper(self, key):
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


    def register(self, object):
        """
        register an object to the main loop
        """
        if not object in self.poll_objects:
            self.poll_objects.append(object)

        
    def unregister(self, object):
        """
        unregister an object from the main loop
        """
        if object in self.poll_objects:
            self.poll_objects.remove(object)

        
    def poll(self):
        """
        main loop
        """
        # run all registered callbacks
        while len(self.one_time_callbacks) > 0:
            callback, arg = self.one_time_callbacks.pop(0)
            callback(*arg)

        # run all registered objects having a poll() function
        # using poll_counter and poll_interval (if given)
        for p in self.poll_objects:
            if hasattr(p, 'poll_counter'):
                if not (self.app and p.poll_menu_only):
                    p.poll_counter += 1
                    if p.poll_counter == p.poll_interval:
                        p.poll_counter = 0
                        p.poll()
            else:
                p.poll()

        # search for events in the queue
        if len(self.queue):
            ret = self.queue[0]
            del self.queue[0]
            return ret

        # search all input objects for new events
        for i in self.inputs:
            e = i.poll(self)
            if e:
                return self.key_event_mapper(e)

        return None


    def subscribe(self, event_callback=None):
        # Only one thing can call poll() so we only handle one subscriber.
        if not event_callback:
            return

        self.event_callback = event_callback
