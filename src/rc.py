# -*- coding: iso-8859-1 -*-
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
# Revision 1.39  2004/07/26 18:10:16  dischi
# move global event handling to eventhandler.py
#
# Revision 1.38  2004/07/25 19:47:38  dischi
# use application and not rc.app
#
# Revision 1.37  2004/07/24 12:22:37  dischi
# move focus handling to rc for now
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


import os
import copy
import time
import thread
import types

import config

from event import Event, BUTTON
import eventhandler

SHUTDOWN = -1

PYLIRC     = False
_singleton = None


def get_singleton():
    """
    get the global rc object
    """
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MainLoop()
        
    return _singleton


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



    def poll(self):
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
                eventhandler.post_key(code)

        
# --------------------------------------------------------------------------------

class Keyboard:
    """
    Class to handle keyboard input
    """
    def __init__(self):
        """
        init the keyboard event handler
        """
        import gui
        self.callback = gui.get_keyboard().poll


    def poll(self):
        """
        return next event
        """
        e = self.callback()
        if e:
            eventhandler.post_key(e)
            

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
        

    def poll(self):
        """
        return next event
        """
        try:
            return self.sock.recv(100)
        except:
            # No data available
            return None


# --------------------------------------------------------------------------------
    
class MainLoop:
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
        except Exception, e:
            print e

        if use_netremote and config.ENABLE_NETWORK_REMOTE and \
               config.REMOTE_CONTROL_PORT:
            self.inputs.append(Network())

        self.callbacks          = []
        self.shutdown_callbacks = []

        # lock all critical parts
        self.lock               = thread.allocate_lock()
        # last time we stopped sleeping
        self.sleep_timer        = 0
        


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


    def run(self):
        eh = eventhandler._singleton
        while 1:
            # wait some time
            duration = 0.01 - (time.time() - self.sleep_timer)
            if duration > 0:
                time.sleep(duration)
            self.sleep_timer = time.time()

            for i in self.inputs:
                e = i.poll()

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

            while eh.queue:
                eh.handle()
                
        return None
