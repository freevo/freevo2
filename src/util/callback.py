# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# callback.py - wrapper for notifier callbacks
# -----------------------------------------------------------------------------
# $Id$
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

__all__ = [ 'call_later', 'remove_callback' ]

# notifier import
import notifier

# internal dict of callbacks
_callbacks = {}

class Callback:
    """
    Internal class handling a callback by name.
    """
    def __init__(self, timer, name, function, *args, **kwargs):
        self.name = name
        self.function = function
        self.args = args
        self.kwargs = kwargs

        if _callbacks.has_key(name):
            notifier.removeTimer()
        self.timer = notifier.addTimer(timer, self)
        _callbacks[name] = self.timer


    def __call__(self):
        """
        Call the callback function.
        """
        # remove from callback
        notifier.removeTimer(self.timer)
        del _callbacks[self.name]
        # call callback function
        self.function(*self.args, **self.kwargs)
        return False


    def remove(self):
        """
        Remove the callback.
        """
        notifier.removeTimer(self.timer)
        del _callbacks[self.name]


def call_later(*args, **kwargs):
    """
    Call a function later from the main loop. If a function is added more
    than once, the timer will be removed and reset. The callback will only
    be called once and removed after that.

    Usage: [ timer ] [ name ] function [ args ]
    If timer is given, the callback will be called from the main loop after
    that timer is expired. If not set, the timer is 0ms. If a name is given,
    this name will be used as internal callback name. If not given, the
    internal name is the function itself. After that, the functions and it's
    paramter can be provided.
    """
    if isinstance(args[0], (int, long)):
        # first parameter is the timer
        timer = args[0]
        args  = args[1:]
    else:
        # no wait
        timer = 0

    if isinstance(args[0], str):
        # first (or second) parameter is a name
        name  = args[0]
        args  = args[1:]
    else:
        # use function as name
        name  = str(args[0])

    # create the Callback
    Callback(timer, name, args[0], *args[1:], **kwargs)
    return True


def remove_callback(name):
    """
    Remove a callback by it's name (or function if no name was given by
    call_later.
    """
    name = str(name)
    if _callbacks.has_key(name):
        notifier.removeTimer(_callbacks[name])
    return True
