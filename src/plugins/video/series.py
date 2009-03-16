# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# artist.py - browse collection based on artist tag
# -----------------------------------------------------------------------------
# $Id: artist.py 11339 2009-03-02 20:09:32Z dmeyer $
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
from item import VideoItem

class SeasonItem(freevo.Item):
    """
    Item for an artist.
    """
    def __init__(self, name, series, season, parent):
        super(SeasonItem, self).__init__(parent)
        self.series = series
        self.season = season
        self.name = name

    @kaa.coroutine()
    def browse(self):
        """
        Show all albums from the artist.
        """
        query = yield kaa.beacon.query(tvdb_series=self.series, tvdb_season=self.season, type='video')
        items = []
        for epsiode in query:
            v = VideoItem(epsiode, self)
            # FIXME: maybe add the episode number
            v.name = epsiode.get('tvdb_title')
            items.append(v)
        self.menustack.pushmenu(freevo.Menu(_('Season'), items, type='video'))

    def actions(self):
        """
        Actions for this item.
        """
        return [ freevo.Action(_('Browse Album from %s') % self.name, self.browse) ]


class SeriesItem(freevo.Item):
    """
    Item for an artist.
    """
    def __init__(self, series, parent):
        super(SeriesItem, self).__init__(parent)
        self.series = series
        self.name = series

    @kaa.coroutine()
    def browse(self):
        """
        Show all albums from the artist.
        """
        query = yield kaa.beacon.query(attr='tvdb_season', tvdb_series=self.series, type='video')
        items = [ SeasonItem(('Season %s') % season, self.series, season, self) for season in query ]
        self.menustack.pushmenu(freevo.Menu(_('Season'), items, type='video'))

    def actions(self):
        """
        Actions for this item.
        """
        return [ freevo.Action(_('Browse Album from %s') % self.name, self.browse) ]


class PluginInterface(freevo.MainMenuPlugin):
    """
    Add 'Browse by Artist' to the audio menu.
    """

    plugin_media = 'video'

    @kaa.coroutine()
    def series(self, parent):
        """
        Show all artists.
        """
        items = []
        for series in (yield kaa.beacon.query(attr='tvdb_series', type='video')):
            items.append(SeriesItem(series, parent))
        parent.menustack.pushmenu(freevo.Menu(_('Series'), items, type='video'))

    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ freevo.ActionItem(_('Browse by TV Series'), parent, self.series) ]
