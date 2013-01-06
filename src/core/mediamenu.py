# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mediamenu.py - Basic menu for all kinds of media
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin can create submenus for the different kind of media
# plugins (video, audio, image)
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003-2009 Dirk Meyer, et al.
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

__all__ = [ 'MediaMenu' ]

# python imports
import os
import time
import logging

# kaa imports
import kaa.beacon
from kaa.weakref import weakref

# freevo imports
import api as freevo

# get logging object
log = logging.getLogger()


class MediaMenu(freevo.MainMenuItem):
    """
    This is the main menu for different media types. It displays the
    default directories, the beacon mountpoints, and sub-plugins.
    """

    __scanning = []

    def __init__(self, parent, title, type, items, subtype=None):
        super(MediaMenu, self).__init__(parent)
        self.media_type = type
        self.media_subtype = subtype
        self.item_menu = None
        kaa.beacon.signals['media.add'].connect_weak(self.media_change)
        kaa.beacon.signals['media.remove'].connect_weak(self.media_change)
        self.name = title
        self._items = items
        for filename in self._items:
            if hasattr(filename, 'scan'):
                self._check_for_rescan(filename.path.replace('$(HOME)', os.environ.get('HOME')), filename.scan)
            if hasattr(filename, 'path'):
                # kaa.config object
                filename = filename.path.replace('$(HOME)', os.environ.get('HOME'))
            filename = os.path.abspath(filename)

    @kaa.coroutine()
    def _check_for_rescan(self, filename, interval):
        """
        Return items for the menu.
        """
        if filename in self.__scanning or not os.path.isdir(filename):
            return
        self.__scanning.append(filename)
        data = (yield kaa.beacon.query(filename=filename)).get()
        if interval == -1:
            log.info('add monitor %s' % filename)
            kaa.beacon.monitor(filename)
        elif data.get('last_crawl', 0) == 0:
            # directory not known, force scan
            log.info('initial scan %s' % filename)
            kaa.beacon.scan(filename)
        elif (time.time() - data.get('last_crawl', 0)) / 3600 > interval:
            # FIXME: if Freevo is running longer than 'interval'
            # hours we need to re-trigger the scan here.
            log.info('scan %s' % filename)
            kaa.beacon.scan(filename)

    @kaa.coroutine()
    def _get_items(self):
        """
        Return items for the menu.
        """
        items = []
        # Add items based on the config file
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
                        items.append(freevo.Directory(d, self, name = title, type = self.media_type))
                    continue
                # normal file
                for p in freevo.MediaPlugin.plugins(self.media_type):
                    p_items = p.get(self, listing)
                    if title:
                        for i in p_items:
                            i.name = title
                    items += p_items
            except:
                log.exception('Error parsing %s' % str(item))
                continue
        # Add items based on beacon mountpoints
        for media in (yield kaa.beacon.list_media()):
            if media.mountpoint == '/':
                continue
            listing = kaa.beacon.wrap(media.root, filter='extmap')
            for p in freevo.MediaPlugin.plugins(self.media_type):
                items.extend(p.get(self, listing))
            for d in listing.get('beacon:dir'):
                items.append(freevo.Directory(d, self, name=media.label, type = self.media_type))
        # Add items from plugins
        for p in freevo.MainMenuPlugin.plugins(self.media_type):
            items += p.items( self )
        yield items

    @kaa.coroutine()
    def select(self):
        """
        Display the media menu
        """
        # generate all other items
        items = yield self._get_items()
        type = '%s main menu' % self.media_type
        item_menu = freevo.Menu(self.name, items, type = type, reload_func = self.reload)
        item_menu.autoselect = True
        self.item_menu = weakref(item_menu)
        self.menustack.pushmenu(item_menu)

    @kaa.coroutine()
    def reload(self):
        """
        Reload the menu. maybe a disc changed or some other plugin.
        """
        if self.item_menu:
            items = yield self._get_items()
            self.item_menu.set_items(items)

    @kaa.coroutine()
    def media_change(self, media):
        """
        Media change from kaa.beacon
        """
        if self.item_menu:
            items = yield self._get_items()
            self.item_menu.set_items(items)

    def eventhandler(self, event):
        """
        Eventhandler for the media menu
        """
        if event == freevo.EJECT and self.item_menu and \
           self.item_menu.selected.info['parent'] == \
           self.item_menu.selected.info['media']:
            self.item_menu.selected.info['media'].eject()
