# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# interface.py - interface between mediamenu and image
# -----------------------------------------------------------------------
# $Id$
#
# This file defines the PluginInterface for the image module
# of Freevo. It is loaded by __init__.py and will activate the
# mediamenu for images.
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/09/13 18:00:50  dischi
# last cleanups for the image module in Freevo
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al.
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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
# ----------------------------------------------------------------------- */

# only export 'PluginInterface' to the outside. This will be used
# with plugin.activate('image') and everything else should be handled
# by using plugin.mimetype()
__all__ = [ 'PluginInterface' ]

# Python imports
import os

# Add support for bins album files
from mmpython.image import bins

# Freevo imports
import config
import util
import plugin

from imageitem import ImageItem
from playlist import Playlist

class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of image items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'image' ]

        # register the callbacks
        plugin.register_callback('fxditem', ['image'], 'slideshow',
                                 self.fxdhandler)

        # activate the mediamenu for image
        level = plugin.is_active('image')[2]
        plugin.activate('mediamenu', level=level, args='image')


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return config.IMAGE_SUFFIX


    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        items = []
        for file in util.find_matches(files, config.IMAGE_SUFFIX):
            items.append(ImageItem(file, parent))
            files.remove(file)
        return items


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on album.xml
        """
        if vfs.isfile(diritem.dir + '/album.xml'):
            # Add album.xml information from bins to the
            # directory informations
            info  = bins.get_bins_desc(diritem.dir)
            if not info.has_key('desc'):
                return

            info = info['desc']
            if info.has_key('sampleimage') and info['sampleimage']:
                # Check if the album.xml defines a sampleimage.
                # If so, use it as image for the directory
                image = vfs.join(diritem.dir, info['sampleimage'])
                if vfs.isfile(image):
                    diritem.image = image

            # set the title from album.xml
            if info.has_key('title') and info['title']:
                diritem.name = info['title']


    def fxdhandler(self, fxd, node):
        """
        parse image specific stuff from fxd files

        <?xml version="1.0" ?>
        <freevo>
          <slideshow title="foo" random="1|0" repeat="1|0">
            <cover-img>foo.jpg</cover-img>
            <background-music random="1|0">
              <directory recursive="1|0">path</directory>
              <file>filename</file>
            </background-music>
            <files>
              <directory recursive="1|0" duration="10">path</directory>
              <file duration="0">filename</file>
            </files>
            <info>
              <description>A nice description</description>
            </info>
          </slideshow>
        </freevo>
        """
        items = []
        dirname = os.path.dirname(fxd.getattr(None, 'filename', ''))
        children = fxd.get_children(node, 'files')
        if children:
            children = children[0].children

        # Create a list of all images for the slideshow
        for child in children:
            try:
                citems = []
                fname  = os.path.join(dirname, String(fxd.gettext(child)))
                if child.name == 'directory':
                    # for directories add all files in it
                    if fxd.getattr(child, 'recursive', 0):
                        f = util.match_files_recursively(fname, self.suffix())
                    else:
                        f = util.match_files(fname, self.suffix())
                    citems = self.get(None, f)

                elif child.name == 'file':
                    # add the given filename
                    citems = self.get(None, [ fname ])

                # set duration until the next images comes up
                duration = fxd.getattr(child, 'duration', 0)
                if duration:
                    for i in citems:
                        i.duration = duration
                items += citems

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
            pl.image = vfs.join(vfs.dirname(fxd.filename), pl.image)


        # background music
        children = fxd.get_children(node, 'background-music')
        if children:
            random   = fxd.getattr(children[0], 'random', 0)
            children = children[0].children

        files  = []
        suffix = []
        for p in plugin.mimetype('audio'):
            suffix += p.suffix()

        for child in children:
            try:
                fname  = os.path.join(dirname, fxd.gettext(child))
                if child.name == 'directory':
                    if fxd.getattr(child, 'recursive', 0):
                        files += util.match_files_recursively(fname, suffix)
                    else:
                        files += util.match_files(fname, suffix)
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
