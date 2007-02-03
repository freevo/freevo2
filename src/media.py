# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# media.py - Media Handling
# -----------------------------------------------------------------------------
# $Id$
#
# Media type handling
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

import plugin

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



def get_plugins(mediatype=None):
    """
    Return all MediaPlugins for the given mediatype. If mediatype
    is None, return all MediaPlugins.
    """
    if not mediatype:
        return plugin.get('media')
    ret = []
    for p in plugin.get('media'):
        if not p.mediatype or mediatype in p.mediatype:
            ret.append(p)
    return ret
