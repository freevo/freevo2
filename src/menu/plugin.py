# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# plugin.py - Plugin interface to the menu
# -----------------------------------------------------------------------------
# $Id: plugin.py 9110 2007-01-31 09:24:06Z dmeyer $
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
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

from freevo.ui import plugin


class ItemPlugin(plugin.Plugin):
    """
    Plugin class to add something to the item action list

    The plugin can also have an eventhandler. All events passed to the item
    will also be passed to this plugin. This works only for VideoItems right
    now (each item type must support it directly). If the function returns
    True, the event won't be passed to other eventhandlers and also not to
    the item itself.
    """
    def __init__(self, name=''):
        plugin.Plugin.__init__(self, name)
        self._plugin_type = 'item'
        self._plugin_special = True


    def actions(self, item):
        """
        return a list of actions to that item. Each action is type Action
        """
        return []


    def eventhandler(self, item, event):
        """
        Additional eventhandler for this item.
        """
        return False
