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
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2011 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

class Action(object):
    """
    Action for item.actions()

    An action has a name and a function to call. Optional parameter is
    a shortcut name to be placed into the config for mapping an action
    to a button. It also has an optional description.

    To set parameters for the function call, use the parameter
    function of the action object. The function itself has always one
    or two parameters. If the function is defined inside the item, no
    extra parameters are used.  If it is outside the item, the first
    parameter is the item.
    """
    def __init__(self, name, function, shortcut=None, description=None, args=None, kwargs=None):
        self.name = name
        self.function = function
        self.shortcut = shortcut
        self.description = description
        self.args = args or []
        self.kwargs = kwargs or {}
        self.item = None

    def __call__(self):
        """
        call the function
        """
        if not self.function:
            return
        # If self.item is set, pass it to the function as first parameter.
        # Check if the function is a member function of that item. If it
        # is, don't pass the item.
        if not self.item or \
                (hasattr(self.function, 'im_self') and self.function.im_self == self.item):
            return self.function(*self.args, **self.kwargs)
        # pass item as first parameter
        return self.function(self.item, *self.args, **self.kwargs)

    def parameter(self, *args, **kwargs):
        """
        Set parameter for the function call.
        """
        self.args = args
        self.kwargs = kwargs
