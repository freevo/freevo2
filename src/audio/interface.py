# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - interface between mediamenu and audio
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines the PluginInterface for the audio module of
# Freevo. It is loaded by __init__.py and will activate the mediamenu
# for audio.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2006 Dirk Meyer, et al.
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

# only export 'PluginInterface' to the outside. This will be used
# with plugin.activate('audio') and everything else should be handled
# by using plugin.mimetype()
__all__ = [ 'PluginInterface' ]

# Python imports
import os
import re
import stat

# Freevo imports
from freevo.ui import config
from freevo.ui import util
from freevo.ui import plugin
from freevo.ui import fxditem

# AudioItem
from audioitem import AudioItem
from audiodiskitem import AudioDiskItem

# fxdhandler for <audio> tags
from fxdhandler import fxdhandler

class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of audio items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'audio' ]

        # add fxd parser callback
        fxditem.add_parser(['audio'], 'audio', fxdhandler)

        # activate the mediamenu for audio
        level = plugin.is_active('audio')[2]
        args = _('Audio Main Menu'), 'audio', config.AUDIO_ITEMS
        plugin.activate('mediamenu', level=level, args=args)


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return [ 'beacon:audio' ] + config.AUDIO_SUFFIX


    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []
        for suffix in self.suffix():
            for file in listing.get(suffix):
                if not file.isfile() and not file.isdir():
                    items.append(AudioDiskItem(file, parent))
                else:
                    items.append(AudioItem(file, parent))
        return items


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        if not diritem.info.has_key('title') and diritem.parent:
            # ok, try some good name creation
            p_album  = diritem.parent['album']
            p_artist = diritem.parent['artist']
            album    = diritem['album']
            artist   = diritem['artist']

            if artist and p_artist == artist and album and not p_album:
                # parent has same artist, but no album, but item has:
                diritem.name = album

            elif not p_artist and not p_album and not artist and album:
                # parent has no info, item no artist but album (== collection)
                diritem.name = album
