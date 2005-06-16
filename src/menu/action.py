# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# action.py - Action class for items
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains an action for items inside the menu. An action has a
# name and a function to call. Optional parameter is a shortcut name to be
# placed into the config for mapping an action to a button. It also has
# an optional description.
#
# To set parameters for the function call, use the parameter function of the
# action object. The function itself has always one or two parameters. If
# the function is defined inside the item, no extra parameters are used.
# If it is outside the item, the first parameter is the item.
#
# Note: Right now there are some fallbacks in Action and also the fake class
# ActionWrapper to support the old style while changing all plugins. This will
# be removed later.
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

class Action:
    """
    Action for item.actions()

    An action has a
    name and a function to call. Optional parameter is a shortcut name to be
    placed into the config for mapping an action to a button. It also has
    an optional description.

    To set parameters for the function call, use the parameter function of the
    action object. The function itself has always one or two parameters. If
    the function is defined inside the item, no extra parameters are used.
    If it is outside the item, the first parameter is the item.
    """
    def __init__(self, name, function, shortcut=None, description=None):
        self.name = name
        self.function = function
        self.shortcut = shortcut
        self.description = description
        self.args = []
        self.kwargs = {}
        self.item = None


    def __call__(self):
        """
        call the function
        """
        if not self.function or not self.item:
            return
        # FIXME: remove this when everything is ported
        if self.kwargs.has_key('arg'):
            return self.function(menuw=self.item.menu.stack,
                                 arg=self.kwargs['arg'])
        # Check if the function is a member function of an item.
        # If it is, do not pass the current item here, it is some
        # sort of comlex submenu
        check_item = self.item
        while check_item:
            if hasattr(self.function, 'im_self') and \
                   self.function.im_self == check_item:
                return self.function(*self.args, **self.kwargs)
            check_item = check_item.parent
        return self.function(self.item, *self.args, **self.kwargs)


    def parameter(self, *args, **kwargs):
        """
        Set parameter for the function call.
        """
        self.args = args
        self.kwargs = kwargs



class ActionWrapper(Action):
    """
    Action for item.actions()
    Note: This will be removed later
    """
    def __init__(self, name, function=None, shortcut=None,
                 description=None):
        Action.__init__(self, name, function, shortcut, description)
        self.function = function


    def __call__(self):
        """
        call the function
        """
        if self.function:
            self.function(menuw=self.item.menu.stack, arg=None)

