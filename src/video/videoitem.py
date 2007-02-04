# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# videoitem.py - Item for video objects
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains a VideoItem. A VideoItem can not only hold a simple
# video file, it can also store subitems if the video is splitted into several
# files. DVD and VCD are also VideoItems.
#
# TODO: o maybe split this file into file/vcd/dvd or
#         move subitem to extra file
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
from freevo.ui import util

from freevo.ui.application import MessageWindow, ConfirmWindow
from freevo.ui.menu import Menu, MediaItem, Files, Action
from freevo.ui.event import *

# video imports
import configure
import database

import player as videoplayer

# get logging object
log = logging.getLogger('video')

# compile VIDEO_SHOW_REGEXP
regexp = config.VIDEO_SHOW_REGEXP
VIDEO_SHOW_REGEXP_MATCH = re.compile("^.*" + regexp).match
VIDEO_SHOW_REGEXP_SPLIT = re.compile("[\.\- ]*" + regexp + "[\.\- ]*").split

class VideoItem(MediaItem):
    def __init__(self, url, parent):
        MediaItem.__init__(self, parent, type='video')

        self.subitems          = []         # more than one file/track to play
        self.current_subitem   = None

        self.subtitle_file     = {}         # text subtitles
        self.audio_file        = {}         # audio dubbing

        self.selected_subtitle = None
        self.selected_audio    = None
        self.elapsed           = 0

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

        if self.name.find(u"The ") == 0:
            self.sort_name = self.name[4:]
        self.sort_name = self.name

        if self.info['episode'] and self.info['subtitle']:
            # get informations for recordings
            show_name = (self.name, '', self.info['episode'], \
                         self.info['subtitle'])
            self.sort_name += u' ' + self.info['episode'] + u' ' + \
                              self.info['subtitle']
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
        if self.mode == 'file' and os.path.isfile(self.filename):
            self.sort_name += u'  ' + str_to_unicode(str(os.stat(self.filename).st_ctime))


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


    def copy(self):
        """
        Create a copy of the VideoItem.
        """
        c = MediaItem.copy(self)
        c.tv_show = False
        return c
    

    def __id__(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        ret = self.url
        if self.subitems:
            for s in self.subitems:
                ret += s.__id__()
        return ret


    def __getitem__(self, key):
        """
        return the specific attribute
        """
        if key == 'geometry' and self.info['width'] and self.info['height']:
            return '%sx%s' % (self.info['width'], self.info['height'])

        if key == 'aspect' and self.info['aspect']:
            aspect = str(self.info['aspect'])
            return aspect[:aspect.find(' ')].replace('/', ':')

        if key  == 'elapsed':
            elapsed = self.elapsed
            if self.info['start']:
                # FIXME: overflow
                elapsed = elapsed - self.info['start']
            if elapsed / 3600:
                return '%d:%02d:%02d' % ( elapsed / 3600,
                                          (elapsed % 3600) / 60,
                                          elapsed % 60)
            else:
                return '%d:%02d' % (int(elapsed / 60), int(elapsed % 60))

        if key == 'runtime':
            length = None

            if self.info['runtime'] and self.info['runtime'] != 'None':
                length = self.info['runtime']
            elif self.info['length'] and self.info['length'] != 'None':
                length = self.info['length']
            if not length and hasattr(self, 'length'):
                length = self.length
            if not length:
                return ''

            if isinstance(length, int) or isinstance(length, float) or \
                   isinstance(length, long):
                length = str(int(round(length) / 60))
            if length.find('min') == -1:
                length = '%s min' % length
            if length.find('/') > 0:
                length = length[:length.find('/')].rstrip()
            if length.find(':') > 0:
                length = length[length.find(':')+1:]
            if length == '0 min':
                return ''
            return length

        return MediaItem.__getitem__(self, key)


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date' and self.mode == 'file' and \
               os.path.isfile(self.filename):
            return u'%s%s' % (os.stat(self.filename).st_ctime,
                              str_to_unicode(self.filename))
        return self.sort_name


    def __set_next_available_subitem(self):
        """
        select the next available subitem. Loops on each subitem and checks if
        the needed media is really there.
        If the media is there, sets self.current_subitem to the given subitem
        and returns 1.
        If no media has been found, we set self.current_subitem to None.
          If the search for the next available subitem did start from the
            beginning of the list, then we consider that no media at all was
            available for any subitem: we return 0.
          If the search for the next available subitem did not start from the
            beginning of the list, then we consider that at least one media
            had been found in the past: we return 1.
        """
        if hasattr(self, 'conf_select_this_item'):
            # XXX bad hack, clean me up
            self.current_subitem = self.conf_select_this_item
            del self.conf_select_this_item
            return True

        cont = 1
        from_start = 0
        si = self.current_subitem
        while cont:
            if not si:
                # No subitem selected yet: take the first one
                si = self.subitems[0]
                from_start = 1
            else:
                pos = self.subitems.index(si)
                # Else take the next one
                if pos < len(self.subitems)-1:
                    # Let's get the next subitem
                    si = self.subitems[pos+1]
                else:
                    # No next subitem
                    si = None
                    cont = 0
        self.current_subitem = None
        return not from_start


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
        self.pushmenu(moviemenu)


    def play(self, **kwargs):
        """
        Play the item.
        """
        if self.subitems:
            # if we have subitems (a movie with more than one file),
            # we start playing the first that is physically available
            self.error_in_subitem = 0
            self.last_error_msg   = ''
            self.current_subitem  = None

            result = self.__set_next_available_subitem()
            if self.current_subitem: # 'result' is always 1 in this case
                # When playing a subitem, the menu must be hidden. If it is
                # not, the playing will stop after the first subitem, since the
                # PLAY_END event is not forwarded to the parent
                # videoitem.
                # And besides, we don't need the menu between two subitems.
                self.last_error_msg=self.current_subitem.play()
                if self.last_error_msg:
                    self.error_in_subitem = 1
                    # Go to the next playable subitem, using the loop in
                    # eventhandler()
                    self.eventhandler(PLAY_END)

            elif not result:
                # No media at all was found: error
                txt = (_('No media found for "%s".\n')+
                       _('Please insert the media.')) % self.name
                box = ConfirmWindow(txt, (_('Retry'), _('Abort')))
                box.buttons[0].connect(self.play)
                box.show()
                
            # done, everything else is handled in 'play' of the subitem
            return

        if self.url.startswith('file://'):
            # normal playback of one file
            file = self.filename

        # call the player to play the item
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
        # PLAY_END: do we have to play another file?
        if self.subitems:
            if event == PLAY_END:
                self.__set_next_available_subitem()
                # Loop until we find a subitem which plays without error
                while self.current_subitem:
                    log.info('playing next item')
                    error = self.current_subitem.play()
                    if error:
                        self.last_error_msg = error
                        self.error_in_subitem = 1
                        self.__set_next_available_subitem()
                    else:
                        return True
                if self.error_in_subitem:
                    # No more subitems to play, and an error occured
                    MessageWindow(self.last_error_msg).show()
        return MediaItem.eventhandler(self, event)
