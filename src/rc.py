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
# Revision 1.41  2004/09/25 04:47:05  rshortt
# Move input classes into input plugins.
#
# Revision 1.40  2004/08/22 20:15:56  dischi
# remove keyboard auto append
#
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

import eventhandler

SHUTDOWN = -1

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

    
class MainLoop:
    """
    Class to transform input keys or buttons into events. This class
    also handles the complete event queue (post_event)
    """
    def __init__(self, use_pylirc=1, use_netremote=1):

        self.inputs = []
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
