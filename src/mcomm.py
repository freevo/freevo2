# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mcomm.py - wrapper for mbus communication for Freevo
# -----------------------------------------------------------------------------
# $Id$
#
# This file registers the application to the mbus and provides some wrapper
# functions and classes for easier access.
#
# Note: this is a test only right now. To test some basic stuff, call
#       './freevo recordserver' and
#       './freevo execute src/tv/recordings.py' in two different shells.
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

# python imports
import os
import sys

# mbus import
from mbus.mbusguides import *

# a list of our callbacks when an entity joins or leaves the bus
_notification_callbacks = []

class Entity:
    """
    Wrapper class for an Entity. It is possible to act with this object like
    it is a real class, only that the calls are handled by the remote
    application.

    There are three different ways to call a function:
    1. add a callback to the end of the paraneter list of a function call
       e.g.: Entity.function_to_call(arg1, arg2, callback)
    2. add the callback as **args to the function:
       e.g.: Entity.function_to_call(arg2, arg2, callback=callback)
    3. provide no callback function and the call will wait for the return
       e.g.: result = Entity.function_to_call(arg2, arg2)
    """
    def __init__(self, addr):
        self.addr = addr
        self.cmd = None
        self.present = True
        
    def __getattr__(self, attr):
        """
        Wrapper function to make it possible to call functions from
        the remote entity.
        """
        if attr in ('has_key', '__getitem__'):
            return getattr(self.addr, attr)
        self.cmd  = attr.replace('_', '-')
        return self.__call

    def __callback(self, return_list, data = None):
        """
        Internal callback when the function should return the resuls.
        """
        self.result = return_list
        
    def __call(self, *args, **kargs):
        """
        Internal function to do the real RPC call.
        """
        if args and callable(args[-1]):
            callback    = args[-1]
            cmdargs     = args[:-1]
            self.result = True
        elif kargs.has_key('callback'):
            callback    = kargs['callback']
            cmdargs     = args
            self.result = True
        else:
            callback    = self.__callback
            cmdargs     = args
            wait        = True
            self.result = None
        _mbus.sendRPC(self.addr, 'home-theatre.' + self.cmd, cmdargs, callback)
        if self.result == True:
            return True
        while not self.result:
            notifier.step(True, False)
        return self.result[0][1:]
        
    def __eq__(self, obj):
        """
        Compare two Entities based on the addr.
        """
        if hasattr(obj, 'addr'):
            obj = obj.addr
        return self.addr == obj

    
def register_entity_notification(func):
    """
    Register to callback to get notification when an entity joins or leaves
    the mbus. The parameter of the callback is an 'Entity'. The attribute
    'present' of this entity can be used to check if the entity joined the
    bus (present = True) or is gone now (present = False).
    """
    _notification_callbacks.append(func)


def register_server(server):
    """
    Register a class as RPC Server. All functions starting with __rpc and
    ending with __ are registered for the specific command.
    """
    for f in dir(server):
        if f.startswith('__rpc_'):
            _mbus.addRPCCallback('home-theatre.' + f[6:-2].replace('_', '-'),
                                 getattr(server, f))
    
def error(description):
    """
    Returns a RPC error for server callbacks.
    """
    return RPCReturn( [], 'FAILED', description )

def result(result, description = 'success'):
    """
    Returns a RPC result for server callbacks.
    """
    return RPCReturn( result, 'OK', description)


# ---------- internal code ---------------------

def _new_entity(maddr):
    """
    pyMbus callback for new entity
    """
    e = Entity(maddr)
    for c in _notification_callbacks:
        c(e)

def _lost_entity(maddr):
    """
    pyMbus callback for lost entity
    """
    e = Entity(maddr)
    e.present = False
    for c in _notification_callbacks:
        c(e)

# create mbus entity for this application
_app = os.path.splitext(os.path.basename(sys.argv[0]))[0]
_mbus = Guidelines( "app:%s lang:python" % _app )
_mbus.newEntityFunction = _new_entity
_mbus.lostEntityFunction = _lost_entity
