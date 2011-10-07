# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mediaitem.py - Item class for items based on media (files)
# -----------------------------------------------------------------------------
# $Id$
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

__all__ = [ 'MediaItem' ]

# python imports
import logging

# kaa imports
import kaa
import kaa.beacon

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
            self.filename = self.url[7:]
            self.files.append(self.filename)

            # FIXME: this is slow. Maybe handle this in the gui code
            # and choose to print self.info.get('name')
            if self.parent and \
                   self.parent['config:use_metadata'] in (None, True):
                self.name = self.info.get('title')
            if not self.name:
                self.name = kaa.str_to_unicode(self.info.get('name'))
        else:
            # Mode is not file, it has to be a network url. Other
            # types like dvd are handled inside the derivated class
            self.filename = ''
            if not self.name:
                self.name = self.info.get('title')
            if not self.name:
                self.name = kaa.str_to_unicode(self.url)

    def _format_time(self, time, hours=False):
        """
        Format time string
        """
        if int(time / 3600) or hours:
            return '%d:%02d:%02d' % ( time / 3600, (time % 3600) / 60, time % 60)
        return '%02d:%02d' % (time / 60, time % 60)

    def get_length(self, style='clock'):
        """
        Return the length of the item as formated unicode string.
        """
        try:
            if style == 'clock':
                return self._format_time(self.info.get('length'))
            if style == 'min':
                return '%d min' % (int(self.info.get('length')) / 60)
            raise AttributeError('unknown length style %s' % style)
        except ValueError:
            return ''

    def get_elapsed(self, style='clock'):
        """
        Return the elapsed time of the item. If style is percent the
        return value is an integer.
        """
        # FIXME: handle elapsed > length
        if style == 'clock':
            try:
                return self._format_time(self.elapsed)
            except ValueError:
                return None
        if style == 'percent':
            try:
                length = int(self.info.get('length'))
                if not hasattr(self, 'elapsed') or not length:
                    return 0
                return min(100 * self.elapsed / length, 100)
            except ValueError:
                return 0
        raise AttributeError('unknown length style %s' % style)

    def get_id(self):
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
        current = MediaItem.get_cfg(self, var.lower()) or 'auto'
        current = choices[(choices.index(current) + 1) % len(choices)]
        self[dbvar] = current
        # change name
        item = self.menustack.current.selected
        item.name = name + '\t'  + current
        # rebuild menu
        self.menustack.refresh(True)

    def configure(self):
        """
        Show the configure dialog for the item.
        """
        items = []
        for i, name, values, descr in self.get_configure_items():
            current = MediaItem.get_cfg(self, i.lower()) or 'auto'
            action = ActionItem(name + '\t'  + current, self,
                                self._set_configure_var, descr)
            action.parameter(var=i, name=name, choices=list(values))
            items.append(action)
        if not items:
            return
        self.menustack.back_submenu(False)
        m = Menu(_('Configure'), items, type='submenu')
        m.table = (80, 20)
        self.menustack.pushmenu(m)
