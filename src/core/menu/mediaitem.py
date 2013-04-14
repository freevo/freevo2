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
import kaa.metadata

# menu imports
from item import Item, ActionItem
from menu import Menu

# get logging object
log = logging.getLogger()


def format_time(time, hours=False):
    """
    Format time string
    """
    if int(time / 3600) or hours:
        return '%d:%02d:%02d' % ( time / 3600, (time % 3600) / 60, time % 60)
    return '%02d:%02d' % (time / 60, time % 60)


class MediaItem(Item):
    """
    This item is for a media. It's only a template for image, video
    or audio items
    """

    elapsed_secs = 0
    __metadata = False

    def __init__(self, parent):
        Item.__init__(self, parent)
        self.url = 'null://'
        self.filename = None

    def set_url(self, url):
        """
        Set a new url to the item and adjust all attributes depending
        on the url. Each MediaItem has to call this function.
        """
        if not isinstance(url, kaa.beacon.Item):
            if not url.startswith('http:'):
                raise RuntimeError('MediaItem.set_url needs a beacon item')
            self.info = {}
            self.url = url
        else:
            self.info = url
            self.url = url.url
        if self.url.startswith('file://'):
            # The url is based on a file. We can search for images
            # and extra attributes here
            self.filename = self.url[7:]
        else:
            # Mode is not file, it has to be a network url. Other
            # types like dvd are handled inside the derivated class
            self.filename = ''
            if not self.name:
                self.name = kaa.str_to_unicode(self.url)

    @property
    def metadata(self):
        """
        kaa.metadata information
        """
        if self.__metadata is False:
            if self.filename is None:
                self.__metadata = None
            else:
                self.__metadata = kaa.metadata.parse(self.filename)
        return self.__metadata

    @property
    def length(self):
        """
        Return the length of the item as formated unicode string.
        """
        try:
            return format_time(self.info.get('length'))
        except ValueError:
            return ''

    @property
    def length_min(self):
        """
        Return the length of the item as formated unicode string.
        """
        try:
            return _('%d min') % (int(self.info.get('length')) / 60)
        except ValueError:
            return ''

    @property
    def elapsed(self):
        """
        Return the elapsed time of the item.
        """
        try:
            return format_time(self.elapsed_secs)
        except ValueError:
            return None

    @property
    def elapsed_percent(self):
        """
        Return the elapsed time of the item.
        """
        try:
            length = int(self.info.get('length'))
            if not self.elapsed_secs or not length:
                return 0
            return min(100 * self.elapsed_secs / length, 100)
        except ValueError:
            return 0

    @property
    def uid(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        return self.url

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

    def __repr__(self):
        """
        Represantation string for debugging
        """
        name = str(self.__class__)
        return "<%s %s>" % (name[name.rfind('.')+1:-2], self.url)
