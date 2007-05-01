# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - interface between mediamenu and video
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines the PluginInterface for the video module of
# Freevo. It is loaded by __init__.py and will activate the mediamenu
# for video.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
import copy
import string

# freevo imports
from freevo import plugin
from freevo.ui import fxditem
from freevo.ui.menu import Files, MediaPlugin
from freevo.ui import config
from freevo.ui.mediamenu import MediaMenu
from freevo.ui.mainmenu import MainMenuPlugin

# video imports
from videoitem import VideoItem
import database
import fxdhandler

class PluginInterface(MediaPlugin, MainMenuPlugin):
    """
    Plugin to handle all kinds of video items
    """
    possible_media_types = [ 'video' ]

    def plugin_activate(self, level):
        """
        Activate the plugin.
        """
        # load the fxd part of video
        fxditem.add_parser(['video'], 'movie', fxdhandler.parse_movie)
        # fxditem.add_parser(['video'], 'disc-set', fxdhandler.parse_disc_set)

        # update the database
        database.update()

        
    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return [ 'beacon:video' ] + config.video.suffix.split(',')


    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []
        for suffix in self.suffix():
            for file in listing.get(suffix):
                items.append(VideoItem(file, parent))
        return items


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        if database.tv_shows.has_key(os.path.basename(diritem.filename).lower()):
            tvinfo = database.tv_shows[os.path.basename(diritem.filename).lower()]
            diritem.info.set_variables(tvinfo[1])
            if not diritem.image:
                diritem.image = tvinfo[0]

    def database(self):
        return database


    def items(self, parent):
        """
        MainMenuPlugin.items to return the video item.
        """
        return [ MediaMenu(parent, _('Video Main Menu'), 'video', config.video.items) ]
