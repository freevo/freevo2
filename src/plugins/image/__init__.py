# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# interface.py - interface between mediamenu and image
# -----------------------------------------------------------------------------
# $Id$
#
# This file defines the PluginInterface for the image module of
# Freevo. It will activate the mediamenu for images.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2009 Dirk Meyer, et al.
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
# with plugin.activate('image') and everything else should be handled
# by using menu.MediaPlugin.plugins()

__all__ = [ 'PluginInterface' ]

# python imports
import os

# kaa imports
import kaa

# freevo imports
from ... import core as freevo
from item import ImageItem


class PluginInterface(freevo.MediaPlugin, freevo.MainMenuPlugin):
    """
    Plugin to handle all kinds of image items
    """
    possible_media_types = [ 'image' ]

    def plugin_activate(self, level):
        """
        Activate the plugin.
        """
        # FIXME: fxdparser is currently broken
        # freevo.add_fxdparser(['image'], 'slideshow', fxdhandler)
        pass

    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return [ 'beacon:image' ] + freevo.config.image.suffix.split(',')

    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []
        for suffix in self.suffix():
            for file in listing.get(suffix):
                items.append(ImageItem(file, parent))
        return items

    def items(self, parent):
        """
        MainMenuPlugin.items to return the image item.
        """
        return [ freevo.MediaMenu(parent, _('Show Images'), 'image', freevo.config.image.items) ]

    def fxdhandler(node, parent, listing):
        """
        Parse audio specific stuff from fxd files::
        """
        fxd = node
        items = []
        dirname = os.path.dirname(fxd.getattr(None, 'filename', ''))
        children = fxd.get_children(node, 'files')
        if children:
            children = children[0].children
        # Create a list of all images for the slideshow
        for child in children:
            try:
                fname  = os.path.join(dirname, kaa.unicode_to_str(fxd.gettext(child)))
                files  = []
                if child.name == 'directory':
                    # for directories add all files in it
                    recursive = fxd.getattr(child, 'recursive', 0)
                    files = freevo.util.match_files(fname, freevo.config.image.suffix.split(','), recursive)
                elif child.name == 'file':
                    # add the given filename
                    files = [ fname ]
                # get duration until the next images comes up
                duration = fxd.getattr(child, 'duration', 0) or freevo.config.image.viewer.duration
                for file in files:
                    items.append(ImageItem(file, None, duration))
            except OSError, e:
                print 'slideshow error:'
                print e
        # create the playlist based on the parsed file list
        pl = freevo.Playlist('', items, fxd.getattr(None, 'parent', None),
               random=fxd.getattr(node, 'random', 0), repeat=fxd.getattr(node, 'repeat', 0))
        pl.autoplay = True
        pl.name = fxd.getattr(node, 'title')
        pl.image = fxd.childcontent(node, 'cover-img')
        if pl.image:
            pl.image = os.path.join(os.path.dirname(fxd.filename), pl.image)
        # background music
        children = fxd.get_children(node, 'background-music')
        if children:
            random   = fxd.getattr(children[0], 'random', 0)
            children = children[0].children
        files  = []
        suffix = []
        for p in freevo.MediaPlugin.plugins('audio'):
            suffix += p.suffix()
        for child in children:
            try:
                fname  = os.path.join(dirname, fxd.gettext(child))
                if child.name == 'directory':
                    recursive = fxd.getattr(child, 'recursive', 0)
                    files += freevo.util.match_files(fname, suffix, recursive)
                elif child.name == 'file':
                    files.append(fname)
            except OSError, e:
                print 'playlist error:'
                print e
        if files:
            pl.background_playlist = freevo.Playlist(playlist=files, random = random, repeat=True, type='audio')
        # add item to list
        fxd.parse_info(fxd.get_children(node, 'info', 1), pl)
        fxd.getattr(None, 'items', []).append(pl)
