# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# artist.py - browse collection based on artist tag
# -----------------------------------------------------------------------------
# $Id: artist.py 11339 2009-03-02 20:09:32Z dmeyer $
#
# This plugin adds an item 'Browse TV Series' to the video menu. The user
# can select an season and after that an episode.
#
# This plugin is also a simple example how to write plugins and how to use
# kaa.beacon in freevo.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2006-2011 Dirk Meyer, et al.
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

# python imports
import logging

# Kaa imports
import kaa
import kaa.beacon
try:
    import kaa.webmetadata
except ImportError:
    kaa.webmetadata = None

# Freevo imports
from ... import core as freevo
from item import VideoItem

# get logging object
log = logging.getLogger('video')


class SeasonItem(freevo.Item):
    """
    Item for an artist.
    """
    def __init__(self, name, series, season, parent):
        super(SeasonItem, self).__init__(parent)
        self.series = series
        self.season = season
        self.name = name
        self.poster = parent.poster

    @kaa.coroutine()
    def browse(self):
        """
        Show all albums from the artist.
        """
        query = yield kaa.beacon.query(series=self.series, season=self.season, type='video')
        items = []
        for epsiode in sorted(query, key=lambda x: x.get('episode')):
            v = VideoItem(epsiode, self)
            v.name = epsiode.get('title')
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

    type = 'series'

    def __init__(self, series, parent):
        super(SeriesItem, self).__init__(parent)
        self.series = series
        self.name = series
        self.poster = None
        if kaa.webmetadata:
            series = kaa.webmetadata.tv.series(self.name)
            if series:
                choice = -1, None
                for poster in series.posters:
                    try:
                        rating = float(poster.data.get('Rating', 0))
                    except ValueError:
                        rating = 0
                    if rating > choice[0]:
                        choice = rating, poster.url
                self.poster = choice[1]
                self.description = series.overview

    @kaa.coroutine()
    def browse(self):
        """
        Show all albums from the artist.
        """
        query = yield kaa.beacon.query(attr='season', series=self.series, type='video')
        items = [ SeasonItem(('Season %s') % season, self.series, season, self) for season in sorted(query)]
        self.menustack.pushmenu(freevo.Menu(_('Season'), items, type='video'))

    def actions(self):
        """
        Actions for this item.
        """
        actions = [ freevo.Action(_('Seasons'), self.browse) ]
        if kaa.webmetadata:
            if not self.description and not self.poster:
                actions.append(freevo.Action(_('Search for metadata'), self.search_metadata))
            else:
                actions.append(freevo.Action(_('Change metadata'), self.search_metadata))
        return actions

    @kaa.coroutine()
    def search_metadata(self):
        actions = []
        msg = freevo.TextWindow(_('Searching'))
        msg.show()
        try:
            for result in (yield kaa.webmetadata.tv.search(None, dict(series=self.name))):
                item = freevo.ActionItem(result.name, self, kaa.Callable(self.set_metadata, result), result.overview)
                if result.posters:
                    item.poster = result.posters[0]
                item.type = 'series'
                actions.append(item)
        except Exception:
            log.exception('search_metadata')
            freevo.Event(freevo.OSD_MESSAGE, _('Error')).post()
            yield
        msg.hide()
        if not actions:
            freevo.Event(freevo.OSD_MESSAGE, _('Series not found')).post()
            self.menustack.back_submenu()
        else:
            self.menustack.pushmenu(freevo.Menu(_('Search Results'), actions, type='video'))

    @kaa.coroutine()
    def set_metadata(self, item, result):
        msg = freevo.TextWindow(_('Fetching Metadata'))
        msg.show()
        try:
            yield kaa.webmetadata.tv.add_series_by_search_result(result, alias=self.name)
        except Exception, e:
            log.exception('error fetching metadata')
            freevo.Event(freevo.OSD_MESSAGE, _('Error')).post()
        msg.hide()
        self.menustack.back_one_menu()
        items = []
        for series in (yield kaa.beacon.query(attr='series', type='video')):
            items.append(SeriesItem(series, self.parent))
        self.menustack.current.set_items(items)

class PluginInterface(freevo.MainMenuPlugin):
    """
    Add 'Browse by TV Series' to the audio menu.
    """

    plugin_media = 'video'

    @kaa.coroutine()
    def show(self, parent):
        """
        Show all series.
        """
        items = []
        for series in (yield kaa.beacon.query(attr='series', type='video')):
            items.append(SeriesItem(series, parent))
        parent.menustack.pushmenu(freevo.Menu(_('Browse TV Series'), items, type='video'))

    def items(self, parent):
        """
        Return the main menu item.
        """
        if freevo.config.video.tv and not parent.media_subtype == 'tv':
            # there is a special TV entry in the main menu but the
            # parent is a different video item
            return []
        return [ freevo.ActionItem(_('Browse TV Series'), parent, self.show) ]
