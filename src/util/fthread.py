# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fthread.py - Freevo threading module
# -----------------------------------------------------------------------------
# $Id$
#
# This module contains some wrapper classes for threading in Freevo. It should
# only be used when non blocking handling is not possible. Freevo itself is not
# thread save, the the function called in the thread should not touch any
# variables inside Freevo which are not protected by by a lock.
#
# There are two ways of using threads with this module:
#
# 1. Using the Thread class. You can create a Thread object with the function
#    and it's arguments. After that you can call the start function to start
#    the thread. This function has an optional parameter with a callback which
#    will be called from the main loop once the thread is finished. The result
#    of the thread function is the parameter for the callback.
#
# 2. Using the 'call' function. The function will call the given function and
#    it's parameter in a thread while keeping the main loop alive. Once the
#    thread is finsihed, the 'call' function returns. Remeber that the main
#    loop is alive during the call (e.g. timer can expire).
#
# In most cases this module is not needed, please add a good reason why you
# wrap a function in a thread. If a thread is used, variant 1 is the prefered
# way of handling threads.
#
# If a thread needs to call a function from the main loop the helper function
# call_from_main can be used. It will schedule the function call in the main
# loop. It is not possible to get the return value of that call.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Version: Dirk Meyer <dmeyer@tzi.de>
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

__all__ = [ 'Thread', 'call', 'call_from_main' ]

# python imports
import copy
import thread
import threading
import notifier
import logging

# get logging object
log = logging.getLogger('fthread')

# internal list of callbacks that needs to be called from the main loop
_callbacks = []
# lock for adding / removing callbacks from _callbacks
_lock = thread.allocate_lock()


class Thread(threading.Thread):
    """
    Notifier aware wrapper for threads.
    """
    def __init__(self, function, *args, **kargs):
        threading.Thread.__init__(self)
        self.callbacks = [ None, None ]
        self.function  = function
        self.args      = args
        self.kargs     = kargs
        self.result    = None
        self.finished  = False
        self.exception = None


    def start(self, callback=None, exception_callback = None):
        """
        Start the thread.
        """
        # append object to list of threads in watcher
        _watcher.append(self)
        # register callback
        self.callbacks = [ callback, exception_callback ]
        # start the thread
        threading.Thread.start(self)


    def run(self):
        """
        Call the function and store the result
        """
        try:
            # run thread function
            self.result = self.function(*self.args, **self.kargs)
        except Exception, e:
            log.exception('Thread crashed:')
            self.exception = e
        # set finished flag
        self.finished = True


    def callback(self):
        """
        Run the callback.
        """
        if self.exception and self.callbacks[1]:
            self.callbacks[1](self.exception)
        elif not self.exception and self.callbacks[0]:
            self.callbacks[0](self.result)


def call(function, *args, **kwargs):
    """
    Run function(*args, **kargs) in a thread and return the result. Keep
    the main loop alive during that time.
    """
    thread = Thread(function, *args, **kwargs)
    thread.start()
    while not thread.finished:
        # step notifier
        notifier.step()
    if thread.exception:
        raise thread.exception
    return thread.result


def call_from_main(function, *args, **kwargs):
    """
    Call a function from the main loop. The function isn't called when this
    function is called, it is called when the watcher in the main loop is
    called by the notifier.
    """
    _lock.acquire()
    _callbacks.append((function, args, kwargs))
    _lock.release()


class Watcher:
    """
    Watcher for running threads.
    """
    def __init__(self):
        self.__threads = []
        self.__timer = None


    def append(self, thread):
        """
        Append a thread to the watcher.
        """
        self.__threads.append(thread)
        if not self.__timer:
            self.__timer = notifier.addTimer( 10, self.check )


    def check(self):
        """
        Check for finished threads and callbacks that needs to be called from
        the main loop.
        """
        finished = []
        # check if callbacks needs to be called from the main loop
        if _callbacks:
            # acquire lock
            _lock.acquire()
            # copy callback list
            cb = copy.copy(_callbacks)
            while _callbacks:
                # delete callbacks
                _callbacks.pop()
            # release lock
            _lock.release()

            # call callback functions
            for function, args, kwargs in cb:
                function(*args, **kwargs)

        for thread in self.__threads:
            # check all threads
            if thread.finished:
                finished.append(thread)

        if not finished:
            # no finished thread, return
            return True

        # check all finished threads
        for thread in finished:
            # remove thread from list
            self.__threads.remove(thread)
            # call callback
            thread.callback()
            # join thread
            thread.join()

        if not self.__threads:
            # remove watcher from notifier
            self.__timer = None
            return False
        return True


# the global watcher object
_watcher = Watcher()
