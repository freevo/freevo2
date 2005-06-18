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

__all__ = [ 'Item' ]

# python imports
import logging
import copy

# freevo imports
import plugin
import mediadb

from util.weakref import weakref

# events covered by item
from event import EJECT

# menu imports (remove this later)
from action import ActionWrapper

# get logging object
log = logging.getLogger()


def _actions_wrapper(actions):
    """
    Bad actions wrapper while porting the menu code.
    This function will be removed later.
    """
    items = []
    for a in actions:
        if isinstance(a, (list, tuple)):
            if len(a) > 3:
                items.append(ActionWrapper(a[1], a[0], a[2], a[3]))
            elif len(a) > 2:
                items.append(ActionWrapper(a[1], a[0], a[2]))
            else:
                items.append(ActionWrapper(a[1], a[0]))
        elif hasattr(a, 'action'):
            items.append(a.action)
        else:
            items.append(a)
    return items



class Item:
    """
    Item class. This is the base class for all items in the menu.
    It's a template for MenuItem and for other info items like
    VideoItem, AudioItem and ImageItem
    """
    def __init__(self, parent=None, action=None, type=None):
        """
        Init the item. Sets all needed variables, if parent is given also
        inherit some settings from there.
        """
        self.icon = None
        self.info = {}
        self.menu = None
        self.type = type

        self.action = action
        if action:
            self.name = action.name
            self.description = action.description
        else:
            self.name = u''
            self.description  = ''
            
        if not hasattr(self, 'autovars'):
            self.autovars = {}

        self.parent = weakref(parent)
        if parent:
            self.image = parent.image
            if parent.type == 'main':
                self.image = None
            self.skin_fxd = parent.skin_fxd
            self.media = parent.media
        else:
            self.image = None
            self.skin_fxd = None
            self.media = None

        self.iscopy = False
        self.fxd_file = None
        self.__initialized = False


    def __setitem__(self, key, value):
        """
        set the value of 'key' to 'val'
        """
        self.info[key] = value


    def store_info(self, key, value):
        """
        store the key/value in metadata
        """
        if isinstance(self.info, mediadb.ItemInfo) and \
               not self.info.store(key, value):
            log.warning( u'unable to store info for \'%s\'' % self.name)


    def delete_info(self, key):
        """
        delete entry for metadata
        """
        if isinstance(self.info, mediadb.ItemInfo):
            return self.info.delete(key)
        return False


    def copy(self):
        """
        Create a copy of the item. This item can be used in submenus of an
        item action. Items like this have self.iscopy = True and the
        original item can be accessed with self.original.
        """
        c = copy.copy(self)
        c.iscopy = True
        if hasattr(self, 'original'):
            c.original = self.original
        else:
            c.original = self
        return c

    
    def __id__(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        return self.name


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        return u'0%s' % self.name


    def actions(self):
        """
        Returns a list of possible actions on this item. The first
        one is autoselected by pressing SELECT
        """
        if self.action:
            return [ self.action ]
        return []

    
    def get_actions(self):
        """
        Get all actions for the item. Do not override this function,
        override 'actions' instead.
        """
        # get actions defined by the item
        items = _actions_wrapper(self.actions())
        # get actions defined by plugins
        plugins = plugin.get('item') + plugin.get('item_%s' % self.type)
        plugins.sort(lambda l, o: cmp(l._level, o._level))
        for p in plugins:
            for a in _actions_wrapper(p.actions(self)):
                # set item for the action
                a.item = self
                items.append(a)
        # FIXME: delete this!
        for i in items:
            i.menuw = self.get_menustack()
        return items


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


    def replace(self, item):
        """
        Replace this item in the menu with the given one.
        """
        self.menu.change_item(self, item)

        
    def eventhandler(self, event, menuw=None):
        """
        Simple eventhandler for an item
        """
        # EJECT event handling
        if self.media and self.media.item == self and event == EJECT:
            self.media.move_tray(dir='toggle')
            return True

        # call eventhandler from plugins
        for p in plugin.get('item') + plugin.get('item_%s' % self.type):
            if p.eventhandler(self, event):
                return True

        # give the event to the next eventhandler in the list
        if self.parent:
            return self.parent.eventhandler(event)

        return False


    def __getitem__(self, attr):
        """
        Return the specific attribute
        """
        if attr[:7] == 'parent(' and attr[-1] == ')' and self.parent:
            return self.parent[attr[7:-1]]

        if attr[:4] == 'len(' and attr[-1] == ')':
            value = self[attr[4:-1]]
            if r == None or r == '':
                return 0
            return len(r)

        r = None
        if self.info.has_key(attr):
            r = self.info[attr]
        if (r == None or r == '') and hasattr(self, attr):
            r = getattr(self,attr)
        if r != None:
            return r
        return ''


    def __init_info__(self):
        """
        Init the info attribute.
        """
        if self.__initialized:
            return False
        self.__initialized = True
        return True
