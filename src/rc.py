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
# Revision 1.21  2003/08/01 13:17:48  outlyer
# Added Matthew Weber's "rc repeat" patch; it requires pylirc 0.0.4 or newer (CVS)
#
# Revision 1.20  2003/07/24 00:12:05  rshortt
# Network remote bugfix.
#
# Revision 1.19  2003/07/12 10:10:56  dischi
# load osd only when needed
#
# Revision 1.18  2003/07/11 02:01:11  rshortt
# Stop freevo from getting double events in some cases.
#
# Revision 1.17  2003/05/30 14:47:32  outlyer
# This wasn't working because you can do:
#
# if (e = something):
#
# since setting the variable doesn't seem to return a true. This version
# works.
#
# Revision 1.16  2003/05/30 00:53:19  rshortt
# Various event bugfixes.
#
# Revision 1.15  2003/05/27 17:53:33  dischi
# Added new event handler module
#
# Revision 1.14  2003/04/27 17:43:30  dischi
# secure RemoteControl against different threads
#
# Revision 1.13  2003/04/27 15:28:24  rshortt
# Adding back support for using a network remote.  If ENABLE_NETWORK_REMOTE is
# set to 1 in local_conf.py then rc.py will also listen for commands over UDP.
#
# Revision 1.12  2003/04/24 19:55:54  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.11  2003/04/20 12:43:32  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.10  2003/04/19 21:28:39  dischi
# identifymedia.py is now a plugin and handles everything related to
# rom drives (init, autostarter, items in menus)
#
# Revision 1.9  2003/04/06 21:12:56  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
#
# Revision 1.7  2003/02/20 18:31:02  dischi
# except on IOError if config.LIRCRC doesn't exists
#
# Revision 1.6  2003/02/19 17:15:15  outlyer
# The idletool needs to know what function we're running so it doesn't try
# to draw when a movie is playing, however, if music is playing, it can still
# draw the information, so we need to distinguish between 'video' and 'audio'
#
# The rc.func will contain the function being used (i.e. 'video' 'audio' etc.)
#
# Currently, this does nothing, so ignore it.
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

import copy
import socket
import config
import util
from event import Event, BUTTON
import osd

PYLIRC = 1
try:
    import pylirc
except ImportError:
    print 'WARNING: PyLirc not found, lirc remote control disabled!'
    PYLIRC = 0

# Set to 1 for debug output
DEBUG = config.DEBUG


TRUE = 1
FALSE = 0

# Module variable that contains an initialized RemoteControl() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = util.SynchronizedObject(RemoteControl())
        
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

    def __init__(self, port=config.REMOTE_CONTROL_PORT):
        self.pylirc = PYLIRC
        self.osd    = osd.get_singleton()
        if self.pylirc:
            try:
                pylirc.init('freevo', config.LIRCRC)
                pylirc.blocking(0)
            except RuntimeError:
                print 'WARNING: Could not initialize PyLirc!'
                self.pylirc = 0
            except IOError:
                print 'WARNING: %s not found!' % config.LIRCRC
                self.pylirc = 0
        if config.ENABLE_NETWORK_REMOTE:
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

        # Take into consideration only 1 event out of ``modulo''
        self.default_repeat_modulo = 4 # Config

        # After how many repeats do we decrease the modulo?
        self.repeat_modulo_decrease_threshhold = 5 # Config
        
        self.repeat_modulo = self.default_repeat_modulo


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
            if flag == 1:
                self.repeat_count = 0
                self.repeat_modulo = self.default_repeat_modulo

            if list != None:
                if self.repeat_count > self.repeat_modulo_decrease_threshhold * \
                  (self.default_repeat_modulo - self.repeat_modulo + 1) \
                  and self.repeat_modulo > 1:
                      self.repeat_modulo -= 1
                if self.repeat_count % self.repeat_modulo != 0:
                    list = []
                self.repeat_count += 1

                for code in list:
                    e = (self.key_event_mapper(code), self.repeat_count)

	            if not e:  e = (self.key_event_mapper(self.osd._cb), None)
                    if e:
                        return e
                
        if config.ENABLE_NETWORK_REMOTE:
            try:
                data = self.sock.recv(100)
                if data == '':
                    print 'Lost the connection'
                    self.conn.close()
                else:
                    return self.key_event_mapper(data)
            except:
                # No data available
                pass

        return (None, None)
