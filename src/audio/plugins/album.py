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
# Copyright (C) 2007 Dirk Meyer, et al.
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
from freevo.ui.mainmenu import MainMenuPlugin
from freevo.ui.menu import Item, ItemList, ActionItem, Menu, Action, GridMenu, MediaItem
from freevo.ui.playlist import Playlist
from freevo.ui.audio import AudioItem
from freevo.ui.directory import DirItem

class AlbumItem(MediaItem):
    """
    Item for on Album (or all) for an artist.
    """
    def __init__(self, artist, album, parent):
        MediaItem.__init__(self, parent)
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
            query = kaa.beacon.query(artist=self.artist, album=self.album, type='audio')
            title = '%s - %s' % (title, kaa.str_to_unicode(self.album))
        else:
            query = kaa.beacon.query(artist=self.artist, type='audio')
        # FIXME: monitor query for live update
        self.playlist = Playlist(title, query, self, type='audio')
        self.playlist.browse()


    def actions(self):
        """
        Actions for this item.
        """
        return [ Action(_('Browse Songs'), self.browse) ]



class ArtistAlbumView(GridMenu):
    """
    Item for an artist.
    """
    def __init__(self, parent):
        GridMenu.__init__(self, _('Artist/Albums View'), type = 'audio grid')
        self.artists_base = 0
        self.artists = []

        # Query all artists.
        # FIXME: yield beacon query
        for artist in kaa.beacon.query(attr='artist', type='audio'):
            self.artists.append(artist)

        self.col_row_swap = False
        self.update()

    def update(self):
        """
        update the guide area
        """
        items = []
        for artist in self.artists:
            # FIXME: monitor query for live update
            # FIXME: yield beacon query
            query = kaa.beacon.query(attr='album', artist=artist, type='audio')
    
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


class PluginInterface(MainMenuPlugin):
    """
    Add 'Browse by Artist albums' to the audio menu.
    """

    def items(self, parent):
        return [ ActionItem(_('Browse by Artists/Albums'), parent, self.show) ]

    def show(self, parent):
        artistalbumview = ArtistAlbumView(parent)
        parent.get_menustack().pushmenu(artistalbumview)
