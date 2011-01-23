# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# videoitem.py - Item for video objects
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains a VideoItem. A VideoItem can not only hold a simple
# video file. DVD and VCD are also VideoItems.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2011 Dirk Meyer, et al.
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

__all__ = [ 'VideoItem', 'VideoPlaylist' ]

# python imports
import logging
import re
import time

# kaa imports
import kaa

# freevo imports
from ... import core as freevo
import configure
import player as videoplayer

# get logging object
log = logging.getLogger('video')

class VideoItem(freevo.MediaItem):
    type = 'video'

    def __init__(self, url, parent):
        super(VideoItem, self).__init__(parent)
        self.user_stop = False
        self.subtitle_file     = {}         # text subtitles
        self.audio_file        = {}         # audio dubbing
        self.selected_subtitle = None
        self.selected_audio    = None
        self.set_url(url)

    def set_url(self, url):
        """
        Sets a new url to the item. Always use this function and not set 'url'
        directly because this functions also changes other attributes, like
        filename and mode
        """
        super(VideoItem, self).set_url(url)
        if self.url.startswith('dvd://') or self.url.startswith('vcd://'):
            if self.info.filename:
                # dvd on harddisc, add '/' for xine
                self.url = self.url + '/'
                self.filename = self.info.filename
                self.files    = freevo.Files()
                self.files.append(self.filename)
            elif self.url.rfind('.iso') + 4 == self.url.rfind('/'):
                # dvd or vcd iso
                self.filename = self.url[5:self.url.rfind('/')]
            else:
                # normal dvd or vcd
                self.filename = ''
        elif self.url.endswith('.iso') and self.info['mime'] == 'video/dvd':
            # dvd iso
            self.mode = 'dvd'
            self.url = 'dvd' + self.url[4:] + '/'
        if self.info['series'] and self.info['season'] and self.info['episode'] and self.info['title']:
            # FIXME: make this a configure option and fix sorting if
            # season is >9
            self.name = '%s %dx%02d - %s' % (
                self.info['series'], self.info['season'], self.info['episode'], self.info['title'])

    def get_geometry(self):
        """
        Return width x height of the image or None
        """
        if self.get('width') and self.get('height'):
            return '%sx%s' % (self.get('width'), self.get('height'))
        return None

    def get_aspect(self):
        """
        Return aspect as string or None if unknown
        """
        if self.info.get('aspect'):
            aspect = str(self.info.get('aspect'))
            return aspect[:aspect.find(' ')].replace('/', ':')
        return None


    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        if self.url.startswith('dvd://') and self.url[-1] == '/':
            items = [ freevo.Action(_('Play DVD'), self.play),
                      freevo.Action(_('DVD title list'), self.dvd_vcd_title_menu) ]
        elif self.url == 'vcd://':
            items = [ freevo.Action(_('Play VCD'), self.play),
                      freevo.Action(_('VCD title list'), self.dvd_vcd_title_menu) ]
        else:
            items = [ freevo.Action(_('Play'), self.play) ]
        # Add the configure stuff (e.g. set audio language)
        return items + configure.get_items(self)

    @kaa.coroutine()
    def dvd_vcd_title_menu(self):
        """
        Generate special menu for DVD/VCD/SVCD content
        """
        # delete the submenu that got us here
        self.menustack.back_submenu(False)
        # build a menu
        items = []
        for track in (yield self.info.list()):
            if not track.get('length') or not track.get('audio'):
                # bad track, skip it
                continue
            track = VideoItem(track, self)
            track.name = _('Play Title %s') % track.info.get('name')
            items.append(track)
        moviemenu = freevo.Menu(self.name, items)
        moviemenu.type = 'video'
        self.menustack.pushmenu(moviemenu)

    def play(self, **kwargs):
        """
        Play the item.
        """
        # call the player to play the item
        self.elapsed = 0
        videoplayer.play(self, **kwargs)

    def stop(self):
        """
        stop playing
        """
        videoplayer.stop()

    def eventhandler(self, event):
        """
        eventhandler for this item
        """
        if event == freevo.STOP:
            self.user_stop = True
        if event == freevo.PLAY_END:
            if not self.user_stop:
                self['last_played'] = int(time.time())
                self.user_stop = False
        super(VideoItem, self).eventhandler(event)


class VideoPlaylist(freevo.Playlist):
    type = 'video'

    def get_id(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        return ''.join([ c.get_id() for c in self.choices ])
