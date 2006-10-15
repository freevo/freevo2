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
# Copyright (C) 2006 Krister Lagerstrom, Dirk Meyer, et al.
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
import kaa.beacon
from kaa.strutils import str_to_unicode

# Freevo imports
from plugin import MainMenuPlugin
from menu import Item, ActionItem, Menu, Action
from playlist import Playlist

class AlbumItem(Item):
    """
    Item for on Album (or all) for an artist.
    """
    def __init__(self, artist, album, parent):
        Item.__init__(self, parent)
        self.artist = artist
        self.album = album
        self.name = _('[ All Songs ]')
        if album:
            self.name = album


    def browse(self):
        """
        Show all items from that artist.
        """
        title = str_to_unicode(self.artist)
        if self.album:
            query = kaa.beacon.query(artist=self.artist, album=self.album)
            title = '%s - %s' % (title, str_to_unicode(self.album))
        else:
            query = kaa.beacon.query(artist=self.artist)
        # FIXME: monitor query for live update
        self.playlist = Playlist(title, query, self, display_type='audio')
        self.playlist.browse()


    def actions(self):
        """
        Actions for this item.
        """
        return [ Action(_('Browse Songs'), self.browse) ]



class ArtistItem(Item):
    """
    Item for an artist.
    """
    def __init__(self, artist, parent):
        Item.__init__(self, parent)
        self.artist = artist

        # Work around a beacon bug
        for part in artist.split(' '):
            self.name += ' ' + str_to_unicode(part.capitalize())
        self.name = self.name.strip()


    def browse(self):
        """
        Show all albums from the artist.
        """
        # FIXME: monitor query for live update
        query = kaa.beacon.query(attr='album', artist=self.artist, type='audio')

        items = [ AlbumItem(self.artist, None, self) ]
        for album in query:
            items.append(AlbumItem(self.artist, album, self))
        self.pushmenu(Menu(_('Album'), items, type='audio'))


    def actions(self):
        """
        Actions for this item.
        """
        return [ Action(_('Browse Album from %s') % self.name, self.browse) ]



class PluginInterface(MainMenuPlugin):
    """
    Add 'Browse by Artist' to the audio menu.
    """

    def artists(self, parent):
        """
        Show all artists.
        """
        items = []
        for artist in kaa.beacon.query(attr='artist', type='audio'):
            items.append(ArtistItem(artist, parent))
        parent.pushmenu(Menu(_('Artists'), items, type='audio'))


    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ ActionItem(_('Browse by Artists'), parent, self.artists) ]
