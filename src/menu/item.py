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

from event import *
from mediadb.globals import *

# get logging object
log = logging.getLogger()

class Item:
    """
    Item class. This is the base class for all items in the menu.
    It's a template for MenuItem and for other info items like
    VideoItem, AudioItem and ImageItem
    """
    def __init__(self, parent=None, info=True):
        """
        Init the item. Sets all needed variables, if parent is given also
        inherit some settings from there.
        """
        if not hasattr(self, 'type'):
            self.type = None

        self.name = u''
        self.icon = None
        self.info = None
        self.menuw = None
        self.description  = ''

        if info:
            # create a basic info object
            self.info = mediadb.item()

        if not hasattr(self, 'autovars'):
            self.autovars = {}

        self.set_parent(parent)
        self.fxd_file = None
        self.__initialized = False

        # FIXME: remove this
        self.defined_actions = self.actions
        self.actions = self.actions_wrapper



    def set_parent(self, parent):
        """
        Set parent for the item.
        """
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


    def __setitem__(self, key, value):
        """
        set the value of 'key' to 'val'
        """
        self.info[key] = value


    def store_info(self, key, value):
        """
        store the key/value in metadata
        """
        if not self.info.store(key, value):
            log.warning( u'unable to store info for \'%s\'' % self.name)


    def delete_info(self, key):
        """
        delete entry for metadata
        """
        return self.info.delete(key)


    def __id__(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        if hasattr(self, 'url'):
            return self.url
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
        return []


    def actions_wrapper(self):
        """
        Bad warpper for actions used while actions is restructured.
        FIXME: remove this function.
        """
        from action import ActionWrapper
        items = []
        for a in self.defined_actions():
            if isinstance(a, (list, tuple)):
                if len(a) > 3:
                    items.append(ActionWrapper(a[1], a[0], a[2], a[3]))
                elif len(a) > 2:
                    items.append(ActionWrapper(a[1], a[0], a[2]))
                else:
                    items.append(ActionWrapper(a[1], a[0]))
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
        if attr == 'length':
            try:
                length = int(self.info['length'])
            except ValueError:
                return self.info['length']
            except:
                try:
                    length = int(self.length)
                except:
                    return ''
            if length == 0:
                return ''
            if length / 3600:
                return '%d:%02d:%02d' % ( length / 3600, (length % 3600) / 60,
                                          length % 60)
            else:
                return '%d:%02d' % (length / 60, length % 60)


        if attr == 'length:min':
            try:
                length = int(self.info['length'])
            except ValueError:
                return self.info['length']
            except:
                try:
                    length = int(self.length)
                except:
                    return ''
            if length == 0:
                return ''
            return '%d min' % (length / 60)

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
