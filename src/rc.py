#if 0 /*
# -----------------------------------------------------------------------
# rc.py - Remote control handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.27  2003/11/02 10:50:15  dischi
# better error handling
#
# Revision 1.26  2003/10/26 17:04:26  dischi
# Patch from Soenke Schwardt to use the time to fix repeat problems with
# some remote receiver.
#
# Revision 1.25  2003/10/18 21:23:38  rshortt
# Added a subscribe method so that you can get a callback when events are
# posted.  Also rework __init__ sligntly.
#
# Revision 1.24  2003/10/14 17:40:11  mikeruelle
# enable network remote to work.
#
# Revision 1.23  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.22  2003/08/23 12:51:41  dischi
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

import os
import copy
import socket
import config
import util
from event import Event, BUTTON
import osd
import time

PYLIRC = 1
try:
    import pylirc
except ImportError:
    print 'WARNING: PyLirc not found, lirc remote control disabled!'
    PYLIRC = 0

# Set to 1 for debug output
DEBUG = config.DEBUG

# Module variable that contains an initialized RemoteControl() object
_singleton = None

def get_singleton(**kwargs):
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = util.SynchronizedObject(RemoteControl(**kwargs))
        
    return _singleton


def post_event(event):
    return get_singleton().post_event(event)


def app(application=0):
    if not application == 0:
        context = 'menu'
        if hasattr(application, 'app_mode'):
            context = application.app_mode
        if hasattr(application, 'eventhandler'):
            application = application.eventhandler
        get_singleton().set_app(application, context)

    return get_singleton().get_app()

def set_context(context):
    get_singleton().set_context(context)


    
class RemoteControl:

    def __init__(self, use_pylirc=1, use_netremote=1):
        self.osd = osd.get_singleton()

        self.use_pylirc = use_pylirc
        if self.use_pylirc:
            self.pylirc = PYLIRC
        else:
            # do not use pylirc if we know we don't want it
            self.pylirc = 0

        if use_netremote and config.ENABLE_NETWORK_REMOTE:
            port = config.REMOTE_CONTROL_PORT
        else:
            port = 0
            use_netremote = 0
        self.use_netremote = use_netremote

        if self.pylirc:
            try:
                if os.path.isfile(config.LIRCRC):
                    pylirc.init('freevo', config.LIRCRC)
                    pylirc.blocking(0)
                else:
                    raise IOError
            except RuntimeError:
                print 'WARNING: Could not initialize PyLirc!'
                self.pylirc = 0
            except IOError:
                print 'WARNING: %s not found!' % config.LIRCRC
                self.pylirc = 0

        if self.use_netremote:
            self.port = port
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setblocking(0)
            self.sock.bind(('', self.port))

        self.app = None
        self.context = 'menu'
        self.queue = []
        self.previous_returned_code = None
        self.previous_code = None;
        self.repeat_count = 0
        self.event_callback = None
        self.firstkeystroke = 0.0
        self.lastkeystroke = 0.0
        self.lastkeycode = ''
        self.default_keystroke_delay1 = 0.25  # Config
        self.default_keystroke_delay2 = 0.25  # Config

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

        print 'no event mapping for key %s in context %s' % (key, self.context)
        print 'send button event BUTTON arg=%s' % key
        return Event(BUTTON, arg=key)
    
    def get_last_code(self):
        result = (None, None) # (Code, is_it_new?)
        if self.previous_code != None:
            # Let's empty the buffer and return the most recent code
            while 1:
                list = pylirc.nextcode();
                if list != []:
                    break
        else:
            list = pylirc.nextcode()
        if list == []:
            # It's a repeat, the flag is 0
            list = self.previous_returned_code
            result = (list, 0)
        elif list != None:
            self.previous_returned_code = list
            # It's a new code (i.e. IR key was released), the flag is 1
            result = (list, 1)
        self.previous_code = list
        return result
        
    def poll(self):
        if len(self.queue):
            ret = self.queue[0]
            del self.queue[0]
            return (ret, None)

        e = self.key_event_mapper(self.osd._cb())
        if e != None:
            return (e, None)
        
        if self.pylirc:
            list, flag = self.get_last_code()

            if list == None:
                nowtime = 0.0
                nowtime = time.time()
                if (self.lastkeystroke + self.default_keystroke_delay2 < nowtime) and (self.firstkeystroke != 0.0):
                    self.firstkeystroke = 0.0
                    self.lastkeystroke = 0.0
                    self.repeat_count = 0
                
            if list != None:
                
                nowtime = time.time()

                if (list != None) and (list != []):
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
                    e = (self.key_event_mapper(code), self.repeat_count)

	            if not e:  e = (self.key_event_mapper(self.osd._cb), None)
                    if e:
                        return e
                
        if self.use_netremote:
            try:
                data = self.sock.recv(100)
                if data == '':
                    print 'Lost the connection'
                    self.conn.close()
                else:
                    return self.key_event_mapper(data), None
            except:
                # No data available
                pass

        return (None, None)

    def subscribe(self, event_callback=None):
        # Only one thing can call poll() so we only handle one subscriber.
        if not event_callback:  return

        self.event_callback = event_callback

