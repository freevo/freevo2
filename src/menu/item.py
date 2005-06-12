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

# freevo imports
import plugin
import mediadb

# events covered by item
from event import EJECT

# menu imports (remove this later)
from action import ActionWrapper

# get logging object
log = logging.getLogger()

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
        self.name = u''
        self.icon = None
        self.info = {}
        self.menuw = None
        self.description  = ''
        self.type = type

        if not hasattr(self, 'autovars'):
            self.autovars = {}

        self.parent = parent
        if parent:
            self.image = parent.image
            if hasattr(parent, 'is_mainmenu_item'):
                self.image = None
            self.skin_fxd = parent.skin_fxd
            self.media = parent.media
        else:
            self.image = None
            self.skin_fxd = None
            self.media = None

        self.fxd_file = None
        self.__initialized = False

        self.action = action
        if action:
            self.name = action.name
            self.description = action.description

        # FIXME: remove this
        self.defined_actions = self.actions
        self.actions = self.actions_wrapper


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
        returns a list of possible actions on this item. The first
        one is autoselected by pressing SELECT
        """
        if self.action:
            return [ self.action ]
        return []


    def actions_wrapper(self):
        """
        Bad warpper for actions used while actions is restructured.
        FIXME: remove this function.
        """
        items = []
        for a in self.defined_actions():
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


    def eventhandler(self, event, menuw=None):
        """
        simple eventhandler for an item
        """
        # EJECT event handling
        if self.media and self.media.item == self and event == EJECT and menuw:
            self.media.move_tray(dir='toggle')
            return True

        # FIXME: evil hack to get the menuw, even when it is not there
        if not menuw:
            menuw = self.menuw

        # call eventhandler from plugins
        for p in plugin.get('item') + plugin.get('item_%s' % self.type):
            if p.eventhandler(self, event, menuw):
                return True

        # give the event to the next eventhandler in the list
        if self.parent:
            return self.parent.eventhandler(event, menuw)

        return False


    def __getitem__(self, attr):
        """
        return the specific attribute
        """
        if attr[:7] == 'parent(' and attr[-1] == ')' and self.parent:
            return self.parent[attr[7:-1]]

        if attr[:4] == 'len(' and attr[-1] == ')':
            r = None
            if self.info.has_key(attr[4:-1]):
                r = self.info[attr[4:-1]]

            if (r == None or r == '') and hasattr(self, attr[4:-1]):
                r = getattr(self,attr[4:-1])
            if r != None:
                return len(r)
            return 0

        else:
            r = None
            if self.info.has_key(attr):
                r = self.info[attr]
            if (r == None or r == '') and hasattr(self, attr):
                r = getattr(self,attr)
            if r != None:
                return r
        return ''


    def delete(self):
        """
        callback when this item is deleted from the menu
        """
        self.parent = None


    def __del__(self):
        """
        delete function of memory debugging
        """
        _mem_debug_('item', self.name)


    def __init_info__(self):
        """
        Init the info attribute.
        """
        if self.__initialized:
            return False
        self.__initialized = True
        if self.info and self.info[mediadb.NEEDS_UPDATE]:
            self.info.cache.parse_item(self.info)
        return True
