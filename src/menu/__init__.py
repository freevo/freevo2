# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# menu.py - freevo menu handling system
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2005-2007 Dirk Meyer, et al.
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

# import the submodules
from files import Files
from item import Item
from listing import ItemList
from mediaitem import MediaItem
from action import Action
from menu import Menu
from stack import MenuStack
from plugin import ItemPlugin, MediaPlugin

class ActionItem(Item, Action):
    """
    A simple item with one action. The first parameter of the function
    passed to this action is always the parent item if not None.
    """
    def __init__(self, name, parent, function, description=''):
        Action.__init__(self, name, function, description=description)
        Item.__init__(self, parent, self)
        self.item = parent
