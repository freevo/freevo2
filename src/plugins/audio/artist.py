# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# artist.py - browse collection based on artist tag
# -----------------------------------------------------------------------------
# $Id$
#
# This plugin adds an item 'Browse by Artists' to the audio menu. The user
# can select an artist and after that an album of that artist (or all).
#
# This plugin is also a simple example how to write plugins and how to use
# kaa.beacon in freevo.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2006-2009 Dirk Meyer, et al.
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

# Kaa imports
import kaa
import kaa.beacon

# Freevo imports
from ... import core as freevo


class AlbumItem(freevo.Item):
    """
    Item for on Album (or all) for an artist.
    """
    def __init__(self, artist, album, parent):
        super(AlbumItem, self).__init__(parent)
        self.artist = artist
        self.album = album
        self.name = _('[ All Songs ]')
        if album:
            self.name = album

    def browse(self):
        """
        Show all items from that artist.
        """
        title = kaa.str_to_unicode(self.artist)
        if self.album:
            query = dict(artist=self.artist, album=self.album, type='audio')
            title = '%s - %s' % (title, kaa.str_to_unicode(self.album))
        else:
            query = dict(artist=self.artist, type='audio')
        # FIXME: monitor query for live update
        async = kaa.beacon.query(**query)
        self.pl = freevo.Playlist(title, async, self, type='audio')
        self.pl.browse()

    def actions(self):
        """
        Actions for this item.
        """
        return [ freevo.Action(_('Browse Songs'), self.browse) ]


class ArtistItem(freevo.Item):
    """
    Item for an artist.
    """
    def __init__(self, artist, parent):
        super(ArtistItem, self).__init__(parent)
        self.artist = artist
        # Work around a beacon bug
        for part in artist.split(' '):
            self.name += ' ' + kaa.str_to_unicode(part.capitalize())
        self.name = self.name.strip()

    @kaa.coroutine()
    def browse(self):
        """
        Show all albums from the artist.
        """
        # FIXME: monitor query for live update
        query = yield kaa.beacon.query(attr='album', artist=self.artist, type='audio')
        items = [ AlbumItem(self.artist, None, self) ]
        for album in query:
            items.append(AlbumItem(self.artist, album, self))
        self.menustack.pushmenu(freevo.Menu(_('Album'), items, type='audio'))

    def actions(self):
        """
        Actions for this item.
        """
        return [ freevo.Action(_('Browse Album from %s') % self.name, self.browse) ]


class PluginInterface(freevo.MainMenuPlugin):
    """
    Add 'Browse by Artist' to the audio menu.
    """

    plugin_media = 'audio'

    @kaa.coroutine()
    def artists(self, parent):
        """
        Show all artists.
        """
        items = []
        for artist in (yield kaa.beacon.query(attr='artist', type='audio')):
            items.append(ArtistItem(artist, parent))
        parent.menustack.pushmenu(freevo.Menu(_('Artists'), items, type='audio'))

    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ freevo.ActionItem(_('Browse by Artists'), parent, self.artists) ]
