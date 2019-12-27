# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# video - interface between mediamenu and video
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines the PluginInterface for the video module of
# Freevo. It will activate the mediamenu for video.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2009 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <https://github.com/Dischi>
# Maintainer:    Dirk Meyer <https://github.com/Dischi>
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

# freevo imports
from ... import core as freevo
from item import VideoItem

# get logging object
log = logging.getLogger('video')


class PluginInterface(freevo.MediaPlugin, freevo.MainMenuPlugin):
    """
    Plugin to handle all kinds of video items
    """
    possible_media_types = [ 'video' ]

    def plugin_activate(self, level):
        """
        Activate the plugin.
        """
        pass

    @property
    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return [ 'beacon:video' ] + freevo.config.video.suffix.split(',')

    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []
        for suffix in self.suffix:
            for file in listing.get(suffix):
                items.append(VideoItem(file, parent))
        return items

    def items(self, parent):
        """
        MainMenuPlugin.items to return the video item.
        """
        items = []
        if freevo.config.video.tv:
            items.append(freevo.MediaMenu(parent, _('Watch a TV Show'), 'video', freevo.config.video.tv, 'tv'))
        if freevo.config.video.movie:
            items.append(freevo.MediaMenu(parent, _('Watch a Movie'), 'video', freevo.config.video.movie, 'movie'))
        if freevo.config.video.misc:
            items.append(freevo.MediaMenu(parent, _('Watch a Video'), 'video', freevo.config.video.misc, 'misc'))
        return items
