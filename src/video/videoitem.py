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
#       o maybe xine options?
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

# freevo imports
import config
import util
import plugin

from gui.windows import MessageBox, ConfirmBox
from menu import Menu, MediaItem, Files, Action
from event import *

# video imports
import configure
import database

# get logging object
log = logging.getLogger('video')

class VideoItem(MediaItem):
    def __init__(self, url, parent):
        MediaItem.__init__(self, parent, type='video')

        self.subitems          = []         # more than one file/track to play
        self.current_subitem   = None

        self.subtitle_file     = {}         # text subtitles
        self.audio_file        = {}         # audio dubbing

        self.mplayer_options   = ''

        self.selected_subtitle = None
        self.selected_audio    = None
        self.elapsed           = 0

        self.player        = None
        self.player_rating = 0

        self.possible_player   = []

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
        elif config.VIDEO_SHOW_REGEXP_MATCH(self.name) and not \
                 self.network_play:
            # split tv show files based on regexp
            show_name = config.VIDEO_SHOW_REGEXP_SPLIT(self.name)
            if show_name[0] and show_name[1] and show_name[2] and show_name[3]:
                self.name = show_name[0] + u" " + show_name[1] + u"x" + \
                            show_name[2] + u" - " + show_name[3]
            else:
                show_name = None

        if show_name:
            # This matches a tv show with a show name, an epsiode and
            # a title of the specific episode
            sn = String(show_name[0].lower())
            if config.VIDEO_SHOW_DATA_DIR:
                image = util.getimage((config.VIDEO_SHOW_DATA_DIR + sn))
                if self.filename and not image:
                    fname = os.path.dirname(self.filename)+'/'+ sn
                    image = util.getimage(fname)
                if image:
                    self.image = image
            if database.tv_shows.has_key(sn):
                tvinfo = database.tv_shows[sn]
                self.info.set_variables(tvinfo[1])
                if not self.image:
                    self.image = tvinfo[0]
                self.mplayer_options = tvinfo[2]
            self.tv_show      = True
            self.show_name    = show_name
            self.tv_show_name = show_name[0]
            self.tv_show_ep   = show_name[3]
        if self.mode == 'file' and os.path.isfile(self.filename):
            self.sort_name += u'  ' + Unicode(os.stat(self.filename).st_ctime)


    def set_url(self, url):
        """
        Sets a new url to the item. Always use this function and not set 'url'
        directly because this functions also changes other attributes, like
        filename, mode and network_play
        """
        MediaItem.set_url(self, url)
        if self.url.startswith('dvd://') or self.url.startswith('vcd://'):
            self.network_play = False
            self.mimetype = self.url[:self.url.find('://')].lower()
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
            self.mimetype = 'dvd'
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
                              Unicode(self.filename))
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


    def __get_possible_player(self):
        """
        return a list of possible player for this item
        """
        possible_player = []
        for p in plugin.getbyname(plugin.VIDEO_PLAYER, True):
            rating = p.rate(self) * 10
            if config.VIDEO_PREFERED_PLAYER == p.name:
                rating += 1
            if hasattr(self, 'force_player') and p.name == self.force_player:
                rating += 100
            possible_player.append((rating, p))
        possible_player.sort(lambda l, o: -cmp(l[0], o[0]))
        return possible_player


    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        self.possible_player = self.__get_possible_player()

        if not self.possible_player:
            self.player = None
            self.player_rating = 0
            return []

        self.player_rating, self.player = self.possible_player[0]

        # For DVD and VCD check if the rating is >= 20. If it is and the url
        # ends with '/', the user should get the DVD/VCD menu from the player.
        # If not, we need to show the title menu.
        if self.url.startswith('dvd://') and self.url[-1] == '/':
            if self.player_rating >= 20:
                items = [ Action(_('Play DVD'), self.play),
                          Action(_('DVD title list'),
                                 self.dvd_vcd_title_menu) ]
            else:
                items = [ Action(_('DVD title list'), self.dvd_vcd_title_menu),
                          Action(_('Play default track'), self.play) ]

        elif self.url == 'vcd://':
            if self.player_rating >= 20:
                items = [ Action(_('Play VCD'), self.play),
                          Action(_('VCD title list'),
                                 self.dvd_vcd_title_menu) ]
            else:
                items = [ Action(_('VCD title list'), self.dvd_vcd_title_menu),
                          Action(_('Play default track'), self.play) ]
        else:
            items = []
            # Add all possible players to the action list
            for r, player in self.possible_player:
                a = Action(_('Play with %s') % player.name, self.play)
                a.parameter(player=player)
                items.append(a)

        # Network play can get a larger cache
        if self.network_play:
            a = Action(_('Play with maximum cache'), self.play)
            a.parameter(mplayer_options='-cache 65536')

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
        for title in range(len(self.info['tracks'])):
            i = copy.copy(self)
            i.parent = self
            # get info
            i.info = self.info.get_subitem(title)
            i.info.filename = self.info.filename
            i.info.url = self.info.url

            i.set_url(i.info)
            i.url = i.url + str(title+1)

            # copy the attributes from kaa.metadata about this track
            i.info.mminfo = self.info.mminfo['tracks'][title]
            i.info.set_variables(self.info.get_variables())
            # set attributes
            i.info_type = 'track'
            i.possible_player = []
            i.files = None
            i.name = Unicode(_('Play Title %s')) % (title+1)
            items.append(i)

        moviemenu = Menu(self.name, items)
        moviemenu.type = 'video'
        self.pushmenu(moviemenu)


    def play(self, player=None, mplayer_options=''):
        """
        Play the item. The argument 'arg' can either be a player or
        extra mplayer arguments.
        """
        if self.subitems:
            # if we have subitems (a movie with more than one file),
            # we start playing the first that is physically available
            self.error_in_subitem = 0
            self.last_error_msg   = ''
            self.current_subitem  = None

            result = self.__set_next_available_subitem()
            if self.current_subitem: # 'result' is always 1 in this case
                # The media is available now for playing
                # Pass along the options, without loosing the subitem's own
                # options
                if self.current_subitem.mplayer_options:
                    if self.mplayer_options:
                        mo = self.current_subitem.mplayer_options
                        mo += ' ' + self.mplayer_options
                        self.current_subitem.mplayer_options = mo
                else:
                    self.current_subitem.mplayer_options = self.mplayer_options
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
                box = ConfirmBox(txt, (_('Retry'), _('Abort')))
                box.connect(0, self.play)
                box.show()
                
            # done, everything else is handled in 'play' of the subitem
            return

        if self.url.startswith('file://'):
            # normal playback of one file
            file = self.filename

        # get the correct player for this item and check the
        # rating if the player can play this item or not
        if not self.possible_player:
            self.possible_player = self.__get_possible_player()

        if not self.possible_player:
            return

        if not self.player:
            # get the best possible player
            self.player_rating, self.player = self.possible_player[0]
            if self.player_rating < 10:
                MessageBox(_('No player for this item found')).show()
                return

        # put together the mplayer options for this file
        mplayer_options = self.mplayer_options.split(' ') + \
                              mplayer_options.split(' ')

        if player:
            self.player = player

        # call all our plugins to let them know we will play
        # FIXME: use a global PLAY event here
        # self.plugin_eventhandler(PLAY)

        # call the player to play the item
        error = self.player.play(mplayer_options, self)

        if error:
            # If we are a subitem we don't show any error message before
            # having tried all the subitems
            if hasattr(self.parent, 'subitems') and self.parent.subitems:
                return error
            else:
                box = MessageBox(error)
                box.connect(self.stop)
                box.show()


    def stop(self):
        """
        stop playing
        """
        if self.player:
            self.player.stop()


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
                    MessageBox(self.last_error_msg).show()

        # show configure menu
        if event == MENU:
            if self.player:
                self.player.stop()
            confmenu = configure.get_menu(self)
            self.pushmenu(confmenu)
            return True

        return MediaItem.eventhandler(self, event)
