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
        freevo.add_fxdparser(['video'], 'movie', self.fxdhandler_movie)
        # FIXME: fxdparser for disc-set is currently broken
        # freevo.add_fxdparser(['video'], 'disc-set', self.fxdhandler_disc)

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
        for suffix in self.suffix():
            for file in listing.get(suffix):
                items.append(VideoItem(file, parent))
        return items

    def items(self, parent):
        """
        MainMenuPlugin.items to return the video item.
        """
        return [ freevo.MediaMenu(parent, _('Watch a Movie'), 'video', freevo.config.video.items) ]

    def fxdhandler_movie(self, node, parent, listing):
        """
        Callback for VideoItem <movie>::

          <?xml version="1.0" ?>
          <freevo>
              <movie title="">
                  <cover-img>file</cover-img>
                  <video>
                      <dvd|vcd|file id name media_id mplayer_options>file</>+
                  <variants>
                      <variant>
                          <part ref mplayer_options>
                              <subtitle media_id>file</subtitle>
                              <audio media_id>file</audio>
                          </part>+
                      </variant>+
                  </variants>
                  <info/>
              </movie>
        """
        files = []
        for c in node.children:
            if c.name != 'video':
                continue
            for f in c.children:
                if f.name != 'file':
                    continue
                filename = kaa.unicode_to_str(f.content)
                # FIXME: make this faster
                for f in listing.get('beacon:all'):
                    if f.get('name') == filename:
                        files.append(f)
                        break
        if len(files) > 1:
            log.error('BEACON_FIXME: VideoItem with more than one file')
            files = [ files[0] ]
        image = node.image
        if len(files) == 0:
            basename = os.path.splitext(node.root.filename)[0]
            for f in listing.get('beacon:all'):
                if getattr(f, 'url') and f.url.startswith('file://') and \
                   os.path.splitext(f.url[7:])[0] == basename:
                    if f.get('type') == 'video':
                        files.append(f)
                    if f.get('type') == 'image' and not image:
                        image = f.url
        # Remove from listing to hide in VideoItem
        # FIXME: make this faster
        for f in files:
            filename = f.get('name')
            ext = os.path.splitext(filename)[1][1:]
            for key in (ext, 'beacon:video'):
                for f in listing.get(key):
                    if f.get('name') == filename:
                        listing.get(key).remove(f)
                        break
        if len(files) == 0:
            log.error('BEACON_FIXME: VideoItem with bad file \n%s', node)
            return None
        item = VideoItem(files[0], parent)
        # Bad hack but works. We can't use the mem: variables in beacon because
        # multiple items based n the same file can have different info. Or maybe
        # we just ignore this. In that case, the fxdinfo code will be replaced by
        # an in beacon solution.
        item.fxdinfo = dict(node.info)
        if node.title:
            item.set_name(node.title)
        # BEACON_FIXME: item.files.fxd_file  = fxd.filename
        if image:
            item.image = image
            # BEACON_FIXME: item.files.image = image
        return item

    def fxdhandler_disc(fxd, node):
        """
        Callback for VideoItem <disc-set>::
          <?xml version="1.0" ?>
          <freevo>
              <disc-set title="">
                  <disc media-id="id"/>
                  <cover-img source="url">file</cover-img>
                  <info/>
              </disc-set>
          </freevo>

        FIXME: this code is currently broken
        """
        item = VideoItem('', fxd.getattr(None, 'parent', None))
        dirname  = os.path.dirname(fxd.filename)
        item.name  = fxd.getattr(node, 'title')
        item.image = fxd.childcontent(node, 'cover-img')
        if item.image:
            item.image = os.path.join(dirname, item.image)
        fxd.parse_info(node, item, {'length': 'runtime'})
        item.__fxd_rom_info__ = True
        item.__fxd_rom_label__ = []
        item.__fxd_rom_id__ = []
        item.__fxd_files_options__ = []
        for disc in fxd.get_children(node, 'disc'):
            id = fxd.getattr(disc, 'media-id')
            if id:
                item.__fxd_rom_id__.append(id)
            label = fxd.getattr(disc, 'label-regexp')
            if label:
                item.__fxd_rom_label__.append(label)
            item.mplayer_options = fxd.getattr(disc, 'mplayer-options')
            there_are_file_opts = 0
            for f in fxd.get_children(disc, 'file-opt'):
                there_are_file_opts = 1
                file_media_id = fxd.getattr(f, 'media-id')
                if not file_media_id:
                    file_media_id = id
                mpl_opts = item.mplayer_options + ' ' + fxd.getattr(f, 'mplayer-options')
                opt = { 'file-id' : file_media_id + fxd.gettext(f), 'mplayer-options': mpl_opts }
                item.__fxd_files_options__.append(opt)
            if there_are_file_opts:
                # in this case, the disc/@mplayer_options is retricted to the set
                # of files defined in the file-opt elements
                item.mplayer_options = ''
        if not item.files:
            item.files = freevo.Files()
        item.files.fxd_file  = fxd.filename
        fxd.getattr(None, 'items', []).append(item)
