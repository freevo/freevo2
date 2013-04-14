# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# LiveTV for the TV menu
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

__all__ = [ 'LiveTVItem' ]

# python imports
import logging

# kaa imports
import kaa

# freevo imports
import freevo2

# FIXME: This is ugly because one plugin imports relative from
# another. This has to change somehow.
from ..video import VideoItem

from channel import Channel

class LiveTVChannel(Channel):

    @kaa.coroutine()
    def select(self):
        url = yield self.backend.stream(self.info)
        VideoItem(url, self).play()


class LiveTVItem(freevo2.MainMenuItem):
    """
    Plugin to handle TV
    """

    def __init__( self, parent, backend):
        super(LiveTVItem, self).__init__(parent, _('Watch Live TV'), 'tv')
        self.backend = backend

    def select(self):
        items = []
        for c in self.backend.channels:
            if not c.get('channelName', ''):
                continue
            items.append(LiveTVChannel(c.get('channelName', ''), self, c, self.backend))
        m = freevo2.Menu(self.name, items, type = 'tv')
        self.menustack.pushmenu(m)
