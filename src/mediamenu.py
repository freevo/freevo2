# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mediamenu.py - Basic menu for all kinds of media
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin can create submenus for the different kind of media plugins.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003-2007 Dirk Meyer, et al.
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

# python imports
import os
import copy
import logging

# kaa imports
import kaa.beacon
from kaa.weakref import weakref

from freevo.ui.event import EJECT
from freevo.ui.directory import DirItem
from freevo.ui.mainmenu import MainMenuItem, MainMenuPlugin
from freevo.ui.menu import Menu, Item, MediaPlugin

# get logging object
log = logging.getLogger()


class MediaMenu(MainMenuItem):
    """
    This is the main menu for different media types. It displays the default
    directories, the beacon mountpoints and sub-plugins.
    """

    def __init__(self, parent, title, type, items):
        super(MediaMenu, self).__init__(parent)
        self.media_type = type
        self.item_menu = None

        kaa.beacon.signals['media.add'].connect_weak(self.media_change)
        kaa.beacon.signals['media.remove'].connect_weak(self.media_change)

        self.name = title

        self._items = items
        for filename in self._items:
            if hasattr(filename, 'path'):
                # kaa.config object
                filename = filename.path.replace('$(HOME)', os.environ.get('HOME'))
            filename = os.path.abspath(filename)
            if os.path.isdir(filename) and \
                   not os.environ.get('NO_CRAWLER') and \
                   not filename == os.environ.get('HOME') and \
                   not filename == '/':
                kaa.beacon.monitor(filename)


    @kaa.coroutine()
    def _get_config_items(self):
        """
        Generate items based on the config settings
        """
        items = []
        for item in self._items:
            try:
                # kaa.config object
                title = unicode(item.name)
                filename = item.path.replace('$(HOME)', os.environ.get('HOME'))
                filename = os.path.abspath(filename)
                listing = (yield kaa.beacon.query(filename=filename)).get(filter='extmap')
                # path is a directory
                if os.path.isdir(filename):
                    for d in listing.get('beacon:dir'):
                        d = DirItem(d, self, name = title, type = self.media_type)
                        items.append(d)
                    continue

                # normal file
                for p in MediaPlugin.plugins(self.media_type):
                    p_items = p.get(self, listing)
                    if title:
                        for i in p_items:
                            i.name = title
                    items += p_items

            except:
                log.exception('Error parsing %s' % str(item))
                continue
        yield items


    def _get_beacon_items(self):
        """
        Generate items based on beacon mountpoints
        """
        items = []
        for media in kaa.beacon.list_media():
            if media.mountpoint == '/':
                continue
            listing = kaa.beacon.wrap(media.root, filter='extmap')
            for p in MediaPlugin.plugins(self.media_type):
                items.extend(p.get(self, listing))
            for d in listing.get('beacon:dir'):
                items.append(DirItem(d, self, name=media.label,
                                     type = self.media_type))
        return items


    def _get_plugin_items(self):
        """
        Generate items based on plugins
        """
        items = []
        for p in MainMenuPlugin.plugins(self.media_type):
            items += p.items( self )
        return items


    @kaa.coroutine()
    def _get_all_items(self):
        """
        Return items for the menu.
        """
        cfg = yield self._get_config_items()
        yield cfg + self._get_beacon_items() + self._get_plugin_items()


    @kaa.coroutine()
    def select(self):
        """
        Display the media menu
        """
        # generate all other items
        items = yield self._get_all_items()
        type = '%s main menu' % self.media_type
        item_menu = Menu(self.name, items, type = type, reload_func = self.reload)
        item_menu.autoselect = True
        self.item_menu = weakref(item_menu)
        self.get_menustack().pushmenu(item_menu)


    @kaa.coroutine()
    def reload(self):
        """
        Reload the menu. maybe a disc changed or some other plugin.
        """
        if self.item_menu:
            items = yield self._get_all_items()
            self.item_menu.set_items(items)


    @kaa.coroutine()
    def media_change(self, media):
        """
        Media change from kaa.beacon
        """
        if self.item_menu:
            items = yield self._get_all_items()
            self.item_menu.set_items(items)


    def eventhandler(self, event):
        """
        Eventhandler for the media menu
        """
        if event == EJECT and self.item_menu and \
           self.item_menu.selected.info['parent'] == \
           self.item_menu.selected.info['media']:
            self.item_menu.selected.info['media'].eject()
