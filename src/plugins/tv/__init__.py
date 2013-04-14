# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# TV plugin
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

__all__ = [ 'PluginInterface' ]

# python imports
import os
import logging

# kaa imports
import kaa
import kaa.beacon

# freevo imports
import freevo2

from livetv import LiveTVItem

# get logging object
log = logging.getLogger('tv')

class TV(freevo2.MainMenuItem):
    """
    MainMenu item as entry point to the TV submenu
    """
    def __init__( self, parent, backend):
        super(TV, self).__init__(parent, _('Watch TV'), 'tv')
        self.backend = backend

    @kaa.coroutine()
    def select(self):
        items = []
        if self.backend:
            # TODO: make sure we are connected before showing this
            # item or we will not have any channels.
            items.append(LiveTVItem(self, self.backend))
            # TODO: add items to add/view/delete recordings
        if freevo2.config.tv.recordings:
            dirname = str(freevo2.config.tv.recordings)
            data = (yield kaa.beacon.query(filename=dirname)).get()
            items.append(freevo2.Directory(data, self, name=_('Recordings'), type='tv'))
        m = freevo2.Menu(self.name, items, type = 'tv')
        m.autoselect = True
        self.menustack.pushmenu(m)


class PluginInterface(freevo2.MainMenuPlugin):
    """
    Plugin to shutdown Freevo from the main menu
    """
    backend = None

    def __init__(self, name=''):
        if not freevo2.config.tv.location == 'main':
            self.plugin_media = 'video'
        super(PluginInterface, self).__init__(name)

    def plugin_activate(self, level):
        exec('import %s as backend' % freevo2.config.tv.backend)
        self.backend = backend.init()

    def items(self, parent):
        if not freevo2.config.tv.location == 'main' and \
                parent.media_subtype != freevo2.config.tv.location:
            return []
        # TODO: if shown inside the video menu show all items directly
        # instead showing the item above.
        if self.backend or freevo2.config.tv.recordings:
            return [ TV(parent, self.backend) ]
        return []
