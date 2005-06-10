# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# action.py - Action class for items
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

# menu imports
from item import Item


class Action(Item):
    """
    Action for item.actions()
    """
    def __init__(self, name, function, shortcut=None, description=None):
        Item.__init__(self)
        self.name = name
        self.function = function
        self.shortcut = shortcut
        self.description = description
        self.args = []
        self.kwargs = {}


    def actions(self):
        """
        Return possible actions when this is handled as item.
        """
        return [ self ]


    def __call__(self, item, menuw):
        """
        call the function
        """
        if not self.function:
            return
        # FIXME: remove this when everything is ported
        if self.kwargs.has_key('arg'):
            return self.function(menuw=menuw, arg=self.kwargs['arg'])
        if hasattr(self.function, 'im_self') and self.function.im_self == item:
            return self.function(menuw, *self.args, **self.kwargs)
        return self.function(item, menuw, *self.args, **self.kwargs)


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


    def __call__(self, item, menuw):
        """
        call the function
        """
        if self.function:
            self.function(menuw=menuw, arg=None)

