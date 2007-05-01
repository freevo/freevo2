# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# item.py - Item class for the menu
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains a basic item for the menu and a special one for items
# based on media content. There is also a base class for actions to be
# returned by the actions() function.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
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

__all__ = [ 'Item', 'ActionItem' ]

# python imports
import logging

# kaa imports
from kaa.weakref import weakref
import kaa.beacon

# menu imports
from plugin import ItemPlugin
from action import Action

# get logging object
log = logging.getLogger()


class Item(object):
    """
    Item class. This is the base class for all items in the menu. It's a
    template for other info items like VideoItem, AudioItem and ImageItem
    """
    type = None

    def __init__(self, parent):
        """
        Init the item. Sets all needed variables, if parent is given also
        inherit some settings from there.
        """
        self.info = {}
        self.menu = None
        self._image = None

        self.name = u''
        self.description  = ''

        if parent:
            self.parent = weakref(parent)
        else:
            self.parent = None

        self.fxd_file = None
        self.__initialized = False


    def _get_image(self):
        if self._image:
            return self._image
        thumb = self.info.get('thumbnail')
        if thumb:
            return thumb.get()
        return None

    def _set_image(self, image):
        self._image = image

    image = property(_get_image, _set_image, None, 'image object')


    def __id__(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same information
        """
        return self.name


    def sort(self, mode='name'):
        """
        Returns the string how to sort this item
        """
        if mode == 'name':
            return self.name
        if mode == 'smart':
            name = self.name
            if name.lower().startswith('the '):
                return name[4:]
            if name.lower().startswith('a '):
                return name[2:]
            return name
        print 'oops', mode, self
        return ''


    def actions(self):
        """
        Returns a list of possible actions on this item. The first
        one is autoselected by pressing SELECT
        """
        return [ Action(self.name, self.select) ]


    def select(self):
        """
        Select the item (default action). Need to be overloaded by the
        inherting item or actions() need to be overloaded.
        """
        raise RuntimeError("no action defined for %s", self)


    def _get_actions(self):
        """
        Get all actions for the item. Do not override this function,
        override 'actions' instead.
        """
        # get actions defined by the item
        post_actions = []
        pre_actions = []
        # get actions defined by plugins
        for p in ItemPlugin.plugins(self.type):
            actions = post_actions
            if p.plugin_level() < 10:
                actions = pre_actions
            for a in p.actions(self):
                # set item for the action
                a.item = self
                actions.append(a)
        return pre_actions + self.actions() + post_actions


    def get_menustack(self):
        """
        Return the menustack this item is associated with. If the item has no
        menu, this function will search the parent to get a possible menustack.
        """
        if self.menu and self.menu.stack:
            return self.menu.stack
        if self.parent:
            return self.parent.get_menustack()
        return None


    def get_submenu(self):
        """
        Return submenu items.
        """
        return [ SubMenuItem(self, a) for a in self._get_actions() ]


    def pushmenu(self, menu):
        """
        Append the given menu to the menu stack this item is associated with
        and set some internal variables.
        """
        menu.item = weakref(self)
        stack = self.get_menustack()
        if not stack:
            raise AttributeError('Item is not bound to a menu stack')
        stack.pushmenu(menu)


    def show_menu(self, refresh=True):
        """
        Go back in the menu stack to the menu showing the item.
        """
        stack = self.get_menustack()
        if not stack or not self.menu:
            raise AttributeError('Item is not bound to a menu stack')
        stack.back_to_menu(self.menu, refresh)


    def replace(self, item):
        """
        Replace this item in the menu with the given one.
        """
        self.menu.change_item(self, item)


    def get_playlist(self):
        """
        Return playlist object.
        """
        if self.parent:
            return self.parent.get_playlist()
        return None


    def eventhandler(self, event):
        """
        Simple eventhandler for an item
        """
        # call eventhandler from plugins
        for p in ItemPlugin.plugins(self.type):
            if p.eventhandler(self, event):
                return True
        # give the event to the next eventhandler in the list
        if self.parent:
            return self.parent.eventhandler(event)
        # nothing to do
        return False


    def __getitem__(self, attr):
        """
        Return the specific attribute
        """
        if attr[:7] == 'parent(' and attr[-1] == ')' and self.parent:
            return self.parent[attr[7:-1]]
        if attr[:4] == 'len(' and attr[-1] == ')':
            value = self[attr[4:-1]]
            if value == None or value == '':
                return 0
            return len(value)
        if attr == 'name':
            return self.name
        r = self.info.get(attr)
        if r in (None, ''):
            r = getattr(self, attr, None)
        return r


    def __setitem__(self, key, value):
        """
        set the value of 'key' to 'val'
        """
        self.info[key] = value



class ActionItem(Item, Action):
    """
    A simple item with one action. The first parameter of the function
    passed to this action is always the parent item if not None.
    """
    def __init__(self, name, parent, function, description=''):
        Item.__init__(self, parent)
        Action.__init__(self, name, function, description=description)
        self.item = parent


    def select(self):
        return self()



class SubMenuItem(Item):
    """
    Item to show an action in a submenu (internal use)
    """
    def __init__(self, parent, action):
        Item.__init__(self, parent)
        self.action = action
        self.name = action.name
        self.description = action.description
        self.image = parent.image


    def actions(self):
        """
        Return the given action.
        """
        return [ self.action ]
