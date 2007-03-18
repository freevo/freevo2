# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fxdhandler - handler for <slideshow> tags in a fxd file
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains the parser for the <slideshow> tag
#
# <?xml version="1.0" ?>
# <freevo>
#     <slideshow title="foo" random="1|0" repeat="1|0">
#         <cover-img>foo.jpg</cover-img>
#         <background-music random="1|0">
#             <directory recursive="1|0">path</directory>
#             <file>filename</file>
#         </background-music>
#         <files>
#             <directory recursive="1|0" duration="10">path</directory>
#             <file duration="0">filename</file>
#         </files>
#         <info>
#             <description>A nice description</description>
#         </info>
#     </slideshow>
# </freevo>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003-2006 Dirk Meyer, et al.
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

__all__ = [ 'fxdhandler' ]

# python imports
import os

# kaa imports
from kaa.strutils import unicode_to_str

# Freevo imports
from freevo.ui.config import config
from freevo.ui import menu

from freevo.ui.util import match_files
from freevo.ui.playlist import Playlist

# ImageItem
from imageitem import ImageItem


def fxdhandler(node, parent, listing):
    """
    Parse image specific stuff from fxd files
    """
    # BEACON_FIXME
    return None

    items = []
    dirname = os.path.dirname(fxd.getattr(None, 'filename', ''))
    children = fxd.get_children(node, 'files')
    if children:
        children = children[0].children

    # Create a list of all images for the slideshow
    for child in children:
        try:
            fname  = os.path.join(dirname, unicode_to_str(fxd.gettext(child)))
            files  = []
            if child.name == 'directory':
                # for directories add all files in it
                recursive = fxd.getattr(child, 'recursive', 0)
                files = match_files(fname, config.image.suffix.split(','), recursive)

            elif child.name == 'file':
                # add the given filename
                files = [ fname ]

            # get duration until the next images comes up
            duration = fxd.getattr(child, 'duration', 0) or \
                       config.image.viewer.duration

            for file in files:
                items.append(ImageItem(file, None, duration))

        except OSError, e:
            print 'slideshow error:'
            print e

    # create the playlist based on the parsed file list
    pl = Playlist('', items, fxd.getattr(None, 'parent', None),
                  random=fxd.getattr(node, 'random', 0),
                  repeat=fxd.getattr(node, 'repeat', 0))
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
    for p in menu.MediaPlugin.plugins('audio'):
        suffix += p.suffix()

    for child in children:
        try:
            fname  = os.path.join(dirname, fxd.gettext(child))
            if child.name == 'directory':
                recursive = fxd.getattr(child, 'recursive', 0)
                files += match_files(fname, suffix, recursive)
            elif child.name == 'file':
                files.append(fname)
        except OSError, e:
            print 'playlist error:'
            print e

    if files:
        bg = Playlist(playlist=files, random = random,
                      repeat=True, display_type='audio')
        pl.background_playlist = bg

    # add item to list
    fxd.parse_info(fxd.get_children(node, 'info', 1), pl)
    fxd.getattr(None, 'items', []).append(pl)
