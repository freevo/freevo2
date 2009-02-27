# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# album.py - browse collection based on album/artist tag
# -----------------------------------------------------------------------------
# $Id: album.py 9541 2007-05-01 18:46:35Z dmeyer $
#
# This plugin adds an item 'Browse by Artists albums' to the audio menu.
# It views the albums per artist in a grid view.
#
# This plugin is also a simple example how to write plugins and how to use
# kaa.beacon in freevo.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2009 Dirk Meyer, et al.
#
# First Edition: Joost <joost.kop@gmail.com>
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

class AlbumItem(freevo.MediaItem):
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

    @kaa.coroutine()
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
        self.playlist = freevo.Playlist(title, async, self, type='audio')
        self.playlist.browse()

    def actions(self):
        """
        Actions for this item.
        """
        return [ freevo.Action(_('Browse Songs'), self.browse) ]


class ArtistAlbumView(freevo.GridMenu):
    """
    Item for an artist.
    """
    def __init__(self, parent):
        super(ArtistAlbumView, self).__init__(_('Artist/Albums View'), type = 'audio grid')
        self.artists_base = 0
        self.artists = []
        self.col_row_swap = False
        self.update()

    @kaa.coroutine()
    def update(self):
        """
        update the guide area
        """
        self.artists = []
        # Query all artists.
        for artist in (yield kaa.beacon.query(attr='artist', type='audio')):
            self.artists.append(artist)
        items = []
        for artist in self.artists:
            # FIXME: monitor query for live update
            # FIXME: yield beacon query
            query = yield kaa.beacon.query(attr='album', artist=artist, type='audio')
            print query
            albums = [ AlbumItem(artist, None, self) ]
            for album in query:
                albums.append(AlbumItem( artist, album, self))

            items.append(albums)
        self.set_items(items)

    def get_column_name(self, col):
        """
        Return the column name
        """
        text = 'Album %s' % (self.base_col+col+1)
        return text

    def get_row_name(self, row):
        """
        Return the row name
        """
        artist_name = ''
        artist = self.artists[self.base_row+row]
        # Work around a beacon bug
        for part in artist.split(' '):
            artist_name += ' ' + kaa.str_to_unicode(part.capitalize())
        artist_name = artist_name.strip()
        return artist_name


class PluginInterface(freevo.MainMenuPlugin):
    """
    Add 'Browse by Artist albums' to the audio menu.
    """

    plugin_media = 'audio'

    def items(self, parent):
        return [ freevo.ActionItem(_('Browse by Artists/Albums'), parent, self.show) ]

    def show(self, parent):
        parent.get_menustack().pushmenu(ArtistAlbumView(parent))
