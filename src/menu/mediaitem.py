# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mediaitem.py - Item class for items based on media (files)
# -----------------------------------------------------------------------------
# $Id$
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

__all__ = [ 'MediaItem' ]

# python imports
import os
import logging
import time

# kaa imports
import kaa.beacon
from kaa.strutils import str_to_unicode

# freevo imports
from freevo.ui.event import PLAY_START, STOP

# menu imports
from item import Item, ActionItem
from files import Files
from menu import Menu

# get logging object
log = logging.getLogger()


class MediaItem(Item):
    """
    This item is for a media. It's only a template for image, video
    or audio items
    """
    def __init__(self, parent):
        Item.__init__(self, parent)
        self.url = 'null://'
        self.filename = None
        self.fxdinfo = {}
        self.elapsed = 0


    def set_url(self, url):
        """
        Set a new url to the item and adjust all attributes depending
        on the url. Each MediaItem has to call this function.
        """
        if not isinstance(url, kaa.beacon.Item):
            raise RuntimeError('MediaItem.set_url needs a beacon item')

        self.info = url
        self.url = url.url
        self.files = Files()
        if self.info.get('read_only'):
            self.files.read_only = True

        self.mode = self.url[:self.url.find('://')]

        if self.mode == 'file':
            # The url is based on a file. We can search for images
            # and extra attributes here
            self.network_play = False
            self.filename     = self.url[7:]
            self.files.append(self.filename)

            # FIXME: this is slow. Maybe handle this in the gui code
            # and choose to print self.info.get('name')
            if self.parent and \
                   self.parent['config:use_metadata'] in (None, True):
                self.name = self.info.get('title')
            if not self.name:
                self.name = str_to_unicode(self.info.get('name'))

        else:
            # Mode is not file, it has to be a network url. Other
            # types like dvd are handled inside the derivated class
            self.network_play = True
            self.filename     = ''
            if not self.name:
                self.name = self.info.get('title')
            if not self.name:
                self.name = str_to_unicode(self.url)


    def format_time(self, time, hours=False):
        """
        Format time string
        """
        if int(time / 3600) or hours:
            return '%d:%02d:%02d' % ( time / 3600, (time % 3600) / 60, time % 60)
        return '%02d:%02d' % (time / 60, time % 60)


    def __getitem__(self, attr):
        """
        return the specific attribute
        """
        if attr.startswith('cfg:'):
            # freevo_config attribute in beacon
            if not self.info.get('freevo_config'):
                return None
            return self['freevo_config'].get(attr[4:])

        if attr.startswith('cache:'):
            # freevo_config attribute in beacon
            if not self.info.get('freevo_cache'):
                return None
            mtime, cache = self.info.get('freevo_cache')
            if mtime == self.info.get('mtime'):
                return cache.get(attr[6:])
            # cache not up-to-date, delete it
            self.info['freevo_cache'] = [ self.info.get('mtime'), {} ]
            return
            
        if attr == 'length':
            try:
                return self.format_time(self.info.get('length'))
            except ValueError:
                return ''

        if attr == 'length:min':
            try:
                return '%d min' % (int(self.info.get('length')) / 60)
            except ValueError:
                return ''

        if attr  == 'elapsed':
            # FIXME: handle elapsed > length
            return self.format_time(self.elapsed)

        if attr == 'elapsed:percent':
            if not hasattr(self, 'elapsed'):
                return 0
            try:
                length = int(self.info.get('length'))
            except ValueError:
                return 0
            if not length:
                return 0
            return min(100 * self.elapsed / length, 100)

        if attr in self.fxdinfo:
            # FIXME: remove this variable and try to make it work using tmp
            # variables in beacon (see video/fxdhandler.py)
            return self.fxdinfo.get(attr)

        return Item.__getitem__(self, attr)


    def __setitem__(self, attr, value):
        """
        Set attribute to value.
        """
        if attr.startswith('cfg:'):
            # freevo_config attribute in beacon
            key = attr[4:]
            if not self.info.get('freevo_config'):
                self.info['freevo_config'] = {}
            self.info['freevo_config'][key] = value
            if self.info.get('tmp:%s' + key):
                # remove tmp setting
                self.info['tmp:%s' + key] = None
            # FIXME: work sround Beacon bug!!!
            self.info['freevo_config'] = dict(self.info['freevo_config'])
            return

        if attr.startswith('cache:'):
            # freevo_config attribute in beacon
            if not self.info.get('freevo_cache') or \
                   self.info.get('freevo_cache')[0] != self.info.get('mtime'):
                self.info['freevo_cache'] = [ self.info.get('mtime'), {} ]
            self.info['freevo_cache'][1][attr[6:]] = value
            # FIXME: work sround Beacon bug!!!
            self.info['freevo_cache'] = self.info['freevo_cache'][:]
            return

        return Item.__setitem__(self, attr, value)


    def __id__(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        return self.url


    def __repr__(self):
        name = str(self.__class__)
        return "<%s %s>" % (name[name.rfind('.')+1:-2], self.url)


    def sort(self, mode='name'):
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            date = self.info.get('date')
            if date:
                return date
            date = self.info.get('mtime')
            if date:
                return date
            return 0
        if mode == 'filename':
            if self.filename:
                return unicode(self.filename, errors = 'replace').lower()
            return self.name.lower()
        return Item.sort(self, mode)


    def cache(self):
        """
        Caches (loads) the next item
        """
        pass


    def play(self):
        """
        Play the item
        """
        pass


    def stop(self):
        """
        Stop playing
        """
        pass


    # ======================================================================
    # configure submenu
    # ======================================================================


    def get_configure_items(self):
        """
        Return configure options for this item.
        """
        raise RuntimeError('item can not be configured')


    def _set_configure_var(self, var, name, choices):
        """
        Update the variable update the menu.
        """
        # update value
        dbvar = 'cfg:%s' % var.lower()
        current = MediaItem.__getitem__(self, dbvar) or 'auto'
        current = choices[(choices.index(current) + 1) % len(choices)]
        self[dbvar] = current
        # change name
        item = self.get_menustack().get_selected()
        item.name = name + '\t'  + current
        # rebuild menu
        self.get_menustack().refresh(True)


    def configure(self):
        """
        Show the configure dialog for the item.
        """
        items = []
        for i, name, values, descr in self.get_configure_items():
            dbvar = 'cfg:%s' % i.lower()
            current = MediaItem.__getitem__(self, dbvar) or 'auto'
            action = ActionItem(name + '\t'  + current, self,
                                self._set_configure_var, descr)
            action.parameter(var=i, name=name, choices=list(values))
            items.append(action)
        if not items:
            return
        self.get_menustack().delete_submenu(False)
        m = Menu(_('Configure'), items)
        m.table = (80, 20)
        self.get_menustack().pushmenu(m)
