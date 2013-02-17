# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# item.py - Item class for the menu
# -----------------------------------------------------------------------------
# This file contains a basic item for the menu and a special one for items
# based on media content. There is also a base class for actions to be
# returned by the actions() function.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2011 Dirk Meyer, et al.
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
from kaa.utils import property

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
    class __metaclass__(type):
        """
        Metaclass to register cached variables
        """
        def __new__(meta, name, bases, attrs):
            cls = type.__new__(meta, name, bases, attrs)
            if hasattr(cls, 'CACHED_ATTRIBUTES'):
                for prop in cls.CACHED_ATTRIBUTES:
                    cls.register_attribute(prop)
                delattr(cls, 'CACHED_ATTRIBUTES')
            if hasattr(cls, 'CACHED_ATTRIBUTES_MTIME'):
                for prop in cls.CACHED_ATTRIBUTES_MTIME:
                    cls.register_attribute(prop, True)
                delattr(cls, 'CACHED_ATTRIBUTES_MTIME')
            return cls

    # item type
    type = None

    class Properties(object):
        """
        Properties class to access the variables from an item as
        simple member. This is used for the GUI code
        """
        def __init__(self, item):
            self.__item = weakref(item)

        def __getattr__(self, attr):
            if not self.__item:
                return None
            return self.__item.get(attr)

    def __init__(self, parent):
        """
        Init the item. Sets all needed variables, if parent is given also
        inherit some settings from there.
        """
        self.__name = u''
        self.__description  = ''
        self.__image = None
        self.info = {}
        self.menu = None
        self.parent = None
        if parent:
            self.parent = weakref(parent)

    @property
    def properties(self):
        return Item.Properties(self)

    @property
    def name(self):
        if not self.__name:
            self.__name = self.info.get('title')
        if not self.__name:
            self.__name = self.info.get('name')
        return self.__name or u''

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def image(self):
        if self.__image:
            return self.__image
        thumb = self.info.get('thumbnail')
        if thumb and not thumb.failed:
            return thumb.image
        return None

    @image.setter
    def image(self, image):
        self.__image = image

    @property
    def description(self):
        return self.__description or self.info.get('description')

    @description.setter
    def description(self, description):
        self.__description = description

    @property
    def uid(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same information
        """
        return self.name

    def get_thumbnail_attribute(self, attribute):
        """
        Return a thumbnail object for the given attribute (e.g. movie
        poster). The attribute must be an image filename.
        """
        if hasattr(self.info, 'get_thumbnail_attribute'):
            return self.info.get_thumbnail_attribute(attribute)

    def sort(self, mode='name'):
        """
        Returns the string how to sort this item
        """
        if mode == 'name' or mode == None:
            return self.name.lower()
        if mode == 'smart':
            name = self.name
            if name.lower().startswith('the '):
                return name[4:].lower()
            if name.lower().startswith('a '):
                return name[2:].lower()
            return name.lower()
        log.error('unsupport sort mode %s', mode)
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
            for a in p.actions_menu(self):
                # set item for the action
                a.item = self
                actions.append(a)
        return pre_actions + self.actions() + post_actions

    @property
    def menustack(self):
        """
        Return the menustack this item is associated with. If the item has no
        menu, this function will search the parent to get a possible menustack.
        """
        if self.menu and self.menu.stack:
            return self.menu.stack
        if self.parent:
            return self.parent.menustack
        return None

    @property
    def subitems(self):
        """
        Return submenu items.
        """
        return [ SubMenuItem(self, a) for a in self._get_actions() ]

    @property
    def cfgitems(self):
        """
        Return configure items.
        """
        configure = []
        for p in ItemPlugin.plugins(self.type):
            configure += p.actions_cfg(self)
        return [ SubMenuItem(self, a) for a in configure ]

    @property
    def playlist(self):
        """
        Return playlist object.
        """
        if hasattr(self.parent, 'choices') and self in self.parent.choices:
            return self.parent
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

    #
    # generic get and set function
    #

    def __get_mtime_attribute(self, attr):
        # freevo_config attribute in beacon
        mtime, cache = self.info.get('freevo_cache', ( 0, {} ))
        if mtime == self.info.get('mtime'):
            return cache.get(attr)
        # cache not up-to-date, delete it
        self.info['freevo_cache'] = [ self.info.get('mtime'), {} ]
        return None

    def __set_mtime_attribute(self, attr, value):
        # freevo_config attribute in beacon
        mtime, cache = self.info.get('freevo_cache', ( 0, {} ))
        if mtime != self.info.get('mtime'):
            print 'clear cache', self
            cache = {}
        cache[attr] = value
        # set again to notify beacon
        self.info['freevo_cache'] = [ mtime, cache ]

    def __get_store_attribute(self, attr, func):
        """
        Return stored config variable value.
        """
        value = self.info.get('freevo_config', {}).get(attr)
        if func:
            value = func(self, attr, value)
        return value

    def __set_store_attribute(self, attr, value):
        store = self.info.get('freevo_config', {})
        store[attr] = value
        # set again to notify beacon
        self.info['freevo_config'] = store

    @classmethod
    def register_attribute(cls, attr, depends_on_mtime=False, func=None):
        """
        Register a new attribute to the item
        """
        if hasattr(cls, attr):
            raise AttributeError('%s already defined' % attr)
        if depends_on_mtime:
            setattr(cls, attr, property(
                    lambda self: cls.__get_mtime_attribute(self, attr),
                    lambda self, value: cls.__set_mtime_attribute(self, attr, value)))
        else:
            setattr(cls, attr, property(
                    lambda self: cls.__get_store_attribute(self, attr, func),
                    lambda self, value: cls.__set_store_attribute(self, attr, value)))
            if func:
                setattr(cls, attr + '__value', property(
                        lambda self: cls.__get_store_attribute(self, attr, None)))

    def get(self, attr):
        """
        Return the specific attribute
        """
        if attr[:4] == 'len(' and attr[-1] == ')':
            value = self[attr[4:-1]]
            if value == None or value == '':
                return 0
            return len(value)
        if attr.find(':') > 0:
            log.warning('using %s is deprecated' % attr)
            # get function with parameter
            keys = attr.split(':')
            func = getattr(self, 'get_' + keys[0], None)
            if func is not None:
                return func(*keys[1:])
        else:
            # get function without parameter
            func = getattr(self, 'get_' + attr, None)
            if func is not None:
                log.warning('using %s is deprecated' % attr)
                return func()
        # try member attribute
        if hasattr(self, attr):
            return getattr(self, attr, None)
        # try beacon
        r = self.info.get(attr)
        if r not in (None, ''):
            return r
        return None

    def __getitem__(self, attr):
        """
        Return the specific attribute
        """
        return self.get(attr)

    def __setitem__(self, key, value):
        """
        Set the value of 'key' to 'val'
        """
        self.info[key] = value



class ActionItem(Item, Action):
    """
    A simple item with one action. The first parameter of the function
    passed to this action is always the parent item if not None.
    """
    def __init__(self, name, parent, function, description='', args=None, kwargs=None):
        Item.__init__(self, parent)
        Action.__init__(self, name, function, description=description, args=args, kwargs=kwargs)
        self.item = parent

    def select(self):
        """
        On select call self.
        """
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
