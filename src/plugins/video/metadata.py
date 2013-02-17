# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Search for metadata
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2013 Dirk Meyer, et al.
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
import sys
import logging

import kaa.webmetadata

# freevo imports
from ... import core as freevo

# the logging object
log = logging.getLogger()

class PluginInterface(freevo.ItemPlugin):
    """
    class to handle metadata
    """

    plugin_media = 'video'

    @kaa.coroutine()
    def search(self, item):
        """
        Search for metadata
        """
        box = freevo.TextWindow('searching')
        box.show()
        result = yield kaa.webmetadata.search(item.filename)
        box.hide()
        items = []
        if not result:
            freevo.Event(freevo.OSD_MESSAGE, _('Nothing found')).post()
            item.menustack.back_submenu()
            yield
        for show in result:
            i = freevo.ActionItem(show.name, item, self.select)
            i.parameter(show)
            i.description = show.overview
            items.append(i)
        item.menustack.pushmenu(freevo.Menu(_('Results'), items, type='video'))

    @kaa.coroutine()
    def select(self, item, choice):
        box = freevo.TextWindow('downloading')
        box.show()
        result = yield kaa.webmetadata.tv.add_series_by_search_result(choice, item.get('series'))
        box.hide()
        item.menustack.back_one_menu()
        # FIXME: missing menu update

    def choose_poster(self, item):
        for p in kaa.webmetadata.parse(item.filename).series.get_all_posters():
            print p.thumbnail
        freevo.Event(freevo.OSD_MESSAGE, _('Not implemented')).post()

    def configure(self, item):
        # FIXME: add more options
        items = [ freevo.ActionItem(_('Replace metadata'), item, self.search) ]
        if len(kaa.webmetadata.parse(item.filename).series.get_all_posters()) > 1:
            items.append(freevo.ActionItem('Choose poster', item, self.choose_poster))
        item.menustack.pushmenu(freevo.Menu(_('Configure metadata'), items, type='submenu'))

    def actions_cfg(self, item):
        """
        Return additional actions for the item.
        """
        if not item.filename:
            return []
        if not item.get('series'):
            # FIXME: add movie search
            return []
        result = kaa.webmetadata.parse(item.filename)
        if result:
            return [ freevo.ActionItem(_('Configure metadata'), item, self.configure) ]
        return [ freevo.ActionItem(_('Search metadata'), item, self.search) ]
