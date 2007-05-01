# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# videoitem.py - Item for video objects
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains a VideoItem. A VideoItem can not only hold a simple
# video file. DVD and VCD are also VideoItems.
#
# TODO: o maybe split this file into file/vcd/dvd or
#       o create better 'arg' handling in play
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

# python imports
import os
import copy
import logging
import re

# kaa imports
from kaa.strutils import unicode_to_str, str_to_unicode

# freevo imports
from freevo.ui import config

from freevo.ui.application import MessageWindow, ConfirmWindow
from freevo.ui.menu import Menu, MediaItem, Files, Action
from freevo.ui.event import PLAY_END

# video imports
import configure
import database

import player as videoplayer

# get logging object
log = logging.getLogger('video')

# compile VIDEO_SHOW_REGEXP
regexp = config.video.show_regexp
VIDEO_SHOW_REGEXP_MATCH = re.compile("^.*" + regexp).match
VIDEO_SHOW_REGEXP_SPLIT = re.compile("[\.\- ]*" + regexp + "[\.\- ]*").split

class VideoItem(MediaItem):
    type = 'video'
    
    def __init__(self, url, parent):
        MediaItem.__init__(self, parent)

        self.subtitle_file     = {}         # text subtitles
        self.audio_file        = {}         # audio dubbing

        self.selected_subtitle = None
        self.selected_audio    = None

        # set url and parse the name
        self.set_url(url)


    def set_name(self, name):
        """
        Set the item name and parse additional informations after title and
        filename is set.
        """
        if name:
            self.name = name
        else:
            self.name = ''
        show_name = None
        self.tv_show = False

        if self.info['episode'] and self.info['subtitle']:
            # get informations for recordings
            show_name = (self.name, '', self.info['episode'], \
                         self.info['subtitle'])
        elif VIDEO_SHOW_REGEXP_MATCH(self.name) and not self.network_play:
            # split tv show files based on regexp
            show_name = VIDEO_SHOW_REGEXP_SPLIT(self.name)
            if show_name[0] and show_name[1] and show_name[2] and show_name[3]:
                self.name = show_name[0] + u" " + show_name[1] + u"x" + \
                            show_name[2] + u" - " + show_name[3]
            else:
                show_name = None

        if show_name:
            # This matches a tv show with a show name, an epsiode and
            # a title of the specific episode
            sn = unicode_to_str(show_name[0].lower())
            if database.tv_shows.has_key(sn):
                tvinfo = database.tv_shows[sn]
                self.info.set_variables(tvinfo[1])
                if not self.image:
                    self.image = tvinfo[0]
            self.tv_show      = True
            self.show_name    = show_name
            self.tv_show_name = show_name[0]
            self.tv_show_ep   = show_name[3]


    def set_url(self, url):
        """
        Sets a new url to the item. Always use this function and not set 'url'
        directly because this functions also changes other attributes, like
        filename, mode and network_play
        """
        MediaItem.set_url(self, url)
        if self.url.startswith('dvd://') or self.url.startswith('vcd://'):
            self.network_play = False
            if self.info.filename:
                # dvd on harddisc, add '/' for xine
                self.url = self.url + '/'
                self.filename = self.info.filename
                self.files    = Files()
                self.files.append(self.filename)
            elif self.url.rfind('.iso') + 4 == self.url.rfind('/'):
                # dvd or vcd iso
                self.filename = self.url[5:self.url.rfind('/')]
            else:
                # normal dvd or vcd
                self.filename = ''

        elif self.url.endswith('.iso') and self.info['mime'] == 'video/dvd':
            # dvd iso
            self.mode     = 'dvd'
            self.url      = 'dvd' + self.url[4:] + '/'
            
        # start name parser by setting name to itself
        self.set_name(self.name)


    def __getitem__(self, key):
        """
        return the specific attribute
        """
        if key == 'geometry' and self.info['width'] and self.info['height']:
            return '%sx%s' % (self.info['width'], self.info['height'])

        if key == 'aspect' and self.info['aspect']:
            aspect = str(self.info['aspect'])
            return aspect[:aspect.find(' ')].replace('/', ':')

        return MediaItem.__getitem__(self, key)


    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        if self.url.startswith('dvd://') and self.url[-1] == '/':
            items = [ Action(_('Play DVD'), self.play),
                      Action(_('DVD title list'), self.dvd_vcd_title_menu) ]
        elif self.url == 'vcd://':
            items = [ Action(_('Play VCD'), self.play),
                      Action(_('VCD title list'), self.dvd_vcd_title_menu) ]
        else:
            items = [ Action(_('Play'), self.play) ]

        # Add the configure stuff (e.g. set audio language)
        items += configure.get_items(self)

        return items


    def dvd_vcd_title_menu(self):
        """
        Generate special menu for DVD/VCD/SVCD content
        """
        # delete the submenu that got us here
        self.get_menustack().delete_submenu(False)

        # build a menu
        items = []
        for track in self.info.list().get():
            if not track.get('length') or not track.get('audio'):
                # bad track, skip it
                continue
            track = VideoItem(track, self)
            track.name = _('Play Title %s') % track.info.get('name')
            items.append(track)
        moviemenu = Menu(self.name, items)
        moviemenu.type = 'video'
        self.get_menustack().pushmenu(moviemenu)


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
