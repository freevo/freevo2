# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# __init__.py - interface between mediamenu and audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.25  2004/07/10 12:33:37  dischi
# header cleanup
#
# Revision 1.24  2004/02/13 17:26:25  dischi
# save coversearch result
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


import os
import re
import stat

import config
import util
import plugin

from audioitem import AudioItem
from audiodiskitem import AudioDiskItem


def cover_filter(x):
    return re.search(config.AUDIO_COVER_REGEXP, x, re.IGNORECASE)


class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of audio items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'audio' ]

        # register the callbacks
        plugin.register_callback('fxditem', ['audio'], 'audio', self.fxdhandler)

        # activate the mediamenu for audio
        plugin.activate('mediamenu', level=plugin.is_active('audio')[2], args='audio')
        

    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return config.AUDIO_SUFFIX


    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        items = []

        for file in util.find_matches(files, config.AUDIO_SUFFIX):
            a = AudioItem(file, parent)
            items.append(a)
            files.remove(file)

        return items


    def dirinfo(self, diritem):
        """
        set informations for a diritem based on the content, etc.
        """
        if not diritem.image:
            timestamp = os.stat(diritem.dir)[stat.ST_MTIME]
            if not diritem['coversearch_timestamp'] or \
                   timestamp > diritem['coversearch_timestamp']:
                # Pick an image if it is the only image in this dir, or it matches
                # the configurable regexp
                files = util.find_matches(vfs.listdir(diritem.dir, include_overlay=True),
                                          ('jpg', 'gif', 'png' ))
                if len(files) == 1:
                    diritem.image = os.path.join(diritem.dir, files[0])
                elif len(files) > 1:
                    covers = filter(cover_filter, files)
                    if covers:
                        diritem.image = os.path.join(diritem.dir, covers[0])
                diritem.store_info('coversearch_timestamp', timestamp)
                diritem.store_info('coversearch_result', diritem.image)
            else:
                diritem.image = diritem['coversearch_result']
                
        if not diritem.info.has_key('title') and diritem.parent:
            # ok, try some good name creation
            p_album  = diritem.parent['album']
            p_artist = diritem.parent['artist']
            album    = diritem['album']
            artist   = diritem['artist']

            if artist and p_artist == artist and album and not p_album:
                # parent has same artist, but no album, but item has:
                diritem.name = album

            # XXX FIXME
            #elif not p_artist and artist:
            #    # item has artist, parent not
            #    diritem.name = artist

            elif not p_artist and not p_album and not artist and album:
                # parent has no info, item no artist but album (== collection)
                diritem.name = album

                
    def fxdhandler(self, fxd, node):
        """
        parse audio specific stuff from fxd files

        <?xml version="1.0" ?>
        <freevo>
          <audio title="Smoothjazz">
            <cover-img>foo.jpg</cover-img>
            <mplayer_options></mplayer_options>
            <player>xine</player>
            <playlist/>
            <reconnect/>
            <url>http://64.236.34.141:80/stream/1005</url>

            <info>
              <genre>JAZZ</genre>
              <description>A nice description</description>
            </info>

          </audio>
        </freevo>

        Everything except title and url is optional. If <player> is set,
        this player will be used (possible xine or mplayer). The tag
        <playlist/> signals that this url is a playlist (mplayer needs that).
        <reconnect/> sihnals that the player should reconnect when the
        connection stopps.
        """
        a = AudioItem('', fxd.getattr(None, 'parent', None), scan=False)

        a.name     = fxd.getattr(node, 'title', a.name)
        a.image    = fxd.childcontent(node, 'cover-img')
        a.url      = fxd.childcontent(node, 'url')
        if a.image:
            a.image = vfs.join(vfs.dirname(fxd.filename), a.image)

        a.mplayer_options  = fxd.childcontent(node, 'mplayer_options')
        if fxd.get_children(node, 'player'):
            a.force_player = fxd.childcontent(node, 'player')
        if fxd.get_children(node, 'playlist'):
            a.is_playlist  = True
        if fxd.get_children(node, 'reconnect'):
            a.reconnect    = True
            
        fxd.parse_info(fxd.get_children(node, 'info', 1), a)
        fxd.getattr(None, 'items', []).append(a)
