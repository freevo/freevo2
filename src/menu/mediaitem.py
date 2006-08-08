# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mediaitem.py - Item class for items based on media (files)
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
# Please see the file doc/CREDITS for a complete list of authors.
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

# freevo imports
from event import *
from sysconfig import Unicode

# menu imports
from item import Item
from files import Files

# get logging object
log = logging.getLogger()


class MediaItem(Item):
    """
    This item is for a media. It's only a template for image, video
    or audio items
    """
    def __init__(self, parent=None, type=None):
        Item.__init__(self, parent, type=type)
        self.url = 'unknown:' + str(self)
        self.filename = None
        self.fxdinfo = {}


    def set_url(self, url):
        """
        Set a new url to the item and adjust all attributes depending
        on the url. Each MediaItem has to call this function.
        """
        if isinstance(url, kaa.beacon.Item):
            self.info = url
            url = url.url
        else:
            log.error('FIXME: bad url %s', url)
            self.info = {}

            self.url = url              # the url itself
            self.network_play = True    # network url, like http
            self.filename     = ''      # filename if it's a file:// url
            self.mode         = ''      # the type (file, http, dvd...)
            self.files        = None    # Files
            self.mimetype     = ''      # extention or mode
            self.name         = u''
            return

        self.url = url
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

            # set the suffix of the file as mimetype
            self.mimetype = self.filename[self.filename.rfind('.')+1:].lower()

            # FIXME: this is slow. Maybe handle this in the gui code
            # and choose to print self.info.get('name')
            if self.parent and \
                   self.parent['config:use_mediaid_tag_names'] in (None, True):
                self.name = self.info.get('title')
            if not self.name:
                self.name = self.info.get('name')

        else:
            # Mode is not file, it has to be a network url. Other
            # types like dvd are handled inside the derivated class
            self.network_play = True
            self.filename     = ''
            self.mimetype     = self.type
            if not self.name:
                self.name = self.info.get('title')
            if not self.name:
                self.name = Unicode(self.url)


    def __getitem__(self, attr):
        """
        return the specific attribute
        """
        if attr == 'length':
            try:
                length = int(self.info.get('length'))
            except ValueError:
                return self.info.get('length')
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
                length = int(self.info.get('length'))
            except ValueError:
                return self.info.get('length')
            except:
                try:
                    length = int(self.length)
                except:
                    return ''
            if length == 0:
                return ''
            return '%d min' % (length / 60)


        if attr == 'elapsed:percent':
            if not hasattr(self, 'elapsed'):
                return 0

            try:
                length = int(self.info.get('length'))
            except ValueError:
                try:
                    length = int(self.length)
                except:
                    return 0
            if not length:
                return 0
            return 100 * self.elapsed / length


        if attr in self.fxdinfo:
            return self.fxdinfo.get(attr)

        return Item.__getitem__(self, attr)


    def __id__(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        return self.url


    def sort(self, mode='name'):
        """
        Returns the string how to sort this item
        """
        if mode == 'date' and self.filename:
            uf = unicode(self.filename, errors = 'replace')
            return u'%s%s' % (os.stat(self.filename).st_ctime, uf)

        return u'0%s' % self.name


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


    def eventhandler(self, event):
        """
        eventhandler for this item
        """
        if event == PLAY_START:
            self['last_played'] = int(time.time())
        return Item.eventhandler(self, event)
