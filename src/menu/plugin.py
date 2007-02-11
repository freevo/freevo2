# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# plugin.py - Plugin interface to the menu
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
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
from freevo.ui import plugin


class ItemPlugin(plugin.Plugin):
    """
    Plugin class to add something to the item action list

    The plugin can also have an eventhandler. All events passed to the item
    will also be passed to this plugin. This works only for VideoItems right
    now (each item type must support it directly). If the function returns
    True, the event won't be passed to other eventhandlers and also not to
    the item itself.
    """
    def __init__(self, name=''):
        plugin.Plugin.__init__(self, name)
        self._plugin_type = 'item'
        self._plugin_special = True


    def actions(self, item):
        """
        return a list of actions to that item. Each action is type Action
        """
        return []


    def eventhandler(self, item, event):
        """
        Additional eventhandler for this item.
        """
        return False


    def plugins(subtype=''):
        """
        Static function to return all ItemPlugins.
        """
        plugins = plugin.get('item')[:]
        if subtype:
            plugins += plugin.get('item_%s' % subtype)
        plugins.sort(lambda l, o: cmp(l._plugin_level, o._plugin_level))
        return plugins

    plugins = staticmethod(plugins)



class MediaPlugin(plugin.Plugin):
    """
    Plugin class for medias handled in a directory/playlist.
    self.mediatype is a list of display types where this media
    should be displayed, [] for always.
    """
    mediatype = []

    def __init__(self, name=''):
        plugin.Plugin.__init__(self, name)
        self._plugin_type = 'media'


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
        for t in self.suffix():
            c += len(listing.get(t))
        return c


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        pass


    def database(self):
        """
        returns a database object
        """
        return None


    def plugins(mediatype=None):
        """
        Static function to return all MediaPlugins for the given mediatype.
        If mediatype is None, return all MediaPlugins.
        """
        if not mediatype:
            return plugin.get('media')
        ret = []
        for p in plugin.get('media'):
            if not p.mediatype or mediatype in p.mediatype:
                ret.append(p)
        return ret

    plugins = staticmethod(plugins)
