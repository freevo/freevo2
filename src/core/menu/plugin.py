# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# plugin.py - Plugin interface to the menu
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007-2011 Dirk Meyer, et al.
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

__all__ = [ 'ItemPlugin', 'MediaPlugin' ]

# freevo imports
from .. import api as freevo

class ItemPlugin(freevo.Plugin):
    """
    Plugin class to add something to the item action list

    The plugin can also have an eventhandler. All events passed to the item
    will also be passed to this plugin. This works only for VideoItems right
    now (each item type must support it directly). If the function returns
    True, the event won't be passed to other eventhandlers and also not to
    the item itself.
    """

    def actions_menu(self, item):
        """
        Return a list of actions to that item for the menu. Each
        action is type Action
        """
        return []

    def actions_cfg(self, item):
        """
        Return a list of actions to that item for the configure
        submenu. Each action is type Action
        """
        return []

    def actions_playback(self, item, player):
        """
        Return a list of actions to that item for a menu during
        playback. Each action is type Action
        """
        return []

    def eventhandler(self, item, event):
        """
        Additional eventhandler for this item.
        """
        return False

    @staticmethod
    def plugins(subtype=''):
        """
        Static function to return all ItemPlugins.
        """
        return [ x for x in ItemPlugin.plugin_list if x.plugin_media in (None, subtype) ]


class MediaPlugin(freevo.Plugin):
    """
    Plugin class for medias handled in a directory/playlist.
    self.possible_media_types is a list of display types where this
    media should be displayed, [] for always.
    """
    possible_media_types = []

    @property
    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return []

    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        return []

    def count(self, parent, listing):
        """
        return how many items will be build on files
        """
        c = 0
        for t in self.suffix:
            c += len(listing.get(t))
        return c

    @staticmethod
    def plugins(media_type=None):
        """
        Static function to return all MediaPlugins for the given media_type.
        If media_type is None, return all MediaPlugins.
        """
        if not media_type:
            return MediaPlugin.plugin_list
        ret = []
        for p in MediaPlugin.plugin_list:
            if not p.possible_media_types or media_type in p.possible_media_types:
                ret.append(p)
        return ret

# register base class
freevo.register_plugin(MediaPlugin)
freevo.register_plugin(ItemPlugin)
