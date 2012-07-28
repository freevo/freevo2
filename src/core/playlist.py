# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# playlist.py - This is the Freevo playlist reading module.
# -----------------------------------------------------------------------------
# $Id$
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

__all__ = [ 'Playlist' ]

# python imports
import random
import os
import copy
import logging

# kaa imports
import kaa
import kaa.beacon
from kaa.utils import property
from kaa.weakref import weakref

# freevo imports
import api as freevo

# get logging object
log = logging.getLogger()

class Playlist(freevo.MediaItem, freevo.ItemList):
    """
    Class for playlists. A playlist can be created with a list of items, a
    filename containing the playlist or a (list of) beacon query(s).
    """

    REPEAT_OFF      = 0
    REPEAT_ITEM     = 1
    REPEAT_PLAYLIST = 2

    type = 'playlist'

    def __init__(self, name='', playlist=[], parent=None, type=None,
                 random=False, autoplay=False, repeat=REPEAT_OFF):
        """
        Init the playlist

        @param playlist:
          - a filename to a playlist file (e.g. m3u)
          - a list of Items, beacon Items or filenames
          - a beacon query
          - an inprogress object pointing to something from the above
        @param type: either a media (video,audio,image) or None for all
        """
        freevo.MediaItem.__init__(self, parent)
        freevo.ItemList.__init__(self)
        self.name = kaa.str_to_unicode(name)
        if self.type == 'tv':
            type = 'video'
        # variables only for Playlist
        self._playlist = playlist
        self.autoplay = autoplay
        self.repeat = repeat
        self.media_type = type
        self.next = None
        self._playlist_valid = playlist == []
        self._random = random
        # create a basic info object
        self.info = {}

    def set_items(self, items, selected=None):
        """
        Set/replace the items.
        """
        super(Playlist, self).set_items(items, selected)
        self._playlist_valid = True

    def _read_m3u(self, plsname, content):
        """
        This is the (m3u) playlist reading function.
        """
        pl_lines = [ l for l in content if not l.startswith('#') ]
        curdir = os.path.dirname(plsname)
        playlist = []
        for line in pl_lines:
            line = line.replace('\\', '/').strip()
            if os.path.exists(os.path.join(curdir,line)):
                playlist.append(os.path.join(curdir,line))
        return playlist

    def _read_pls(self, plsname, content):
        """
        This is the (pls) playlist reading function.

        Arguments: plsname  - the playlist filename
        Returns:   The list of interesting lines in the playlist
        """
        pl_lines = [ l for l in content if l.startswith('File') ]
        for pos, line in enumerate(pl_lines):
            numchars=line.find("=")+1
            if numchars > 0:
                pl_lines[pos] = line[numchars:]
        curdir = os.path.dirname(plsname)
        playlist = []
        for line in pl_lines:
            line = line.replace('\\', '/').strip()
            if os.path.exists(os.path.join(curdir,line)):
                playlist.append(os.path.join(curdir,line))
        return playlist

    @kaa.coroutine(policy=kaa.POLICY_SINGLETON)
    def _playlist_create_items(self):
        """
        Build the playlist. Create a list of items and filenames. This function
        will load the playlist file or expand directories
        """
        self._playlist_valid = True
        items = []
        if isinstance(self._playlist, kaa.InProgress):
            # something not finished, wait
            # This may happen for a beacon query
            self._playlist = yield self._playlist
        if isinstance(self._playlist, (str, unicode)):
            # playlist is a filename, load the file and create playlist
            self.set_url(self._playlist)
            log.info('create playlist for %s' % self._playlist)
            try:
                f = open(self._playlist)
                content = map(lambda l: l.strip(' \n\r'), f.readlines())
                f.close()
                if content and content[0].find("[playlist]") > -1:
                    self._playlist = self._read_pls(self._playlist, content)
                else:
                    self._playlist = self._read_m3u(self._playlist, content)
            except (OSError, IOError), e:
                log.error('playlist error: %s' % e)
                self._playlist = []
        if isinstance(self._playlist, kaa.beacon.Query):
            self._playlist = [ self._playlist ]
        # Note: playlist is a list of Items, strings (filenames) or a
        # beacon query now.
        plugins = freevo.MediaPlugin.plugins(self.media_type)
        for item in self._playlist:
            if isinstance(item, freevo.Item):
                # Item object, correct parent
                item = copy.copy(item)
                item.parent = weakref(self)
                items.append(item)
                continue
            if not isinstance(item, kaa.beacon.Query):
                # make item a beacon query
                item = yield kaa.beacon.query(filename=item)
            playlist = []
            fitems = item.get(filter='extmap')
            for p in plugins:
                playlist.extend(p.get(self, fitems))
            # sort beacon query on url
            playlist.sort(lambda x,y: cmp(x.url, y.url))
            # add to playlist
            items.extend(playlist)
        self.set_items(items, 0)
        self._playlist = []

    def _randomize(self):
        """
        resort the playlist by random
        """
        if not self._random:
            return False
        playlist = self.choices
        randomized = []
        while playlist:
            element = random.choice(playlist)
            playlist.remove(element)
            randomized.append(element)
        self.set_items(randomized, 0)
        return True

    def get(self, attr):
        """
        return the specific attribute
        """
        if not self._playlist_valid:
            self._playlist_create_items()
        return freevo.MediaItem.get(self, attr)

    def actions(self):
        """
        return the actions for this item: play and browse
        """
        browse = freevo.Action(_('Browse Playlist'), self.browse)
        play = freevo.Action(_('Play'), self.play)
        if self.autoplay:
            items = [ play, browse ]
        else:
            items = [ browse, play ]
        if not self._random:
            items.append(freevo.Action(_('Random play all items'), self._play_random))
        return items

    @kaa.coroutine()
    def browse(self):
        """
        show the playlist in the menu
        """
        if not self._playlist_valid:
            yield self._playlist_create_items()
        # randomize if needed
        self._randomize()
        menu = freevo.Menu(self.name, self.choices, type = self.media_type)
        self.menustack.pushmenu(menu)

    @kaa.coroutine()
    def play(self):
        """
        play the playlist
        """
        if not self._playlist_valid:
            yield self._playlist_create_items()
        if not self.choices:
            log.warning('empty playlist')
            yield False
        self._randomize()
        self.next = self.choices[0]
        freevo.PLAY_START.post(self)
        self._play_next()

    def _play_random(self):
        """
        play the playlist in random order
        """
        Playlist(playlist=self.choices, parent=self.parent,
                 type=self.media_type, random=True,
                 repeat=self.repeat).play()

    def _play_next(self):
        """
        Play the next item (defined by self.next).
        """
        self.select(self.next)
        if hasattr(self.selected, 'play'):
            # play the item
            self.selected.play()
            return True
        # The item has no play function. It would be possible to just
        # get all actions and select the first one, but this won't be
        # right. Maybe this action opens a menu and nothing more. So
        # it is play or skip.
        if self.next is not None:
            return self._play_next(self)
        return True

    def stop(self):
        """
        stop playing
        """
        self.next = None
        if self.selected:
            self.selected.stop()

    def select(self, item):
        """
        Select item that is playing right now.
        """
        freevo.ItemList.select(self, item)
        if self.selected is None:
            return False
        if self.selected.menu and self.selected in self.selected.menu.choices:
            # update menu
            self.selected.menu.select(self.selected)
        # get next item
        pos = (self.selected_pos+1) % len(self.choices)
        if pos == 0 and not self.repeat == Playlist.REPEAT_PLAYLIST:
            self.next = None
        else:
            self.next = self.choices[pos]

    def eventhandler(self, event):
        """
        Handle playlist specific events
        """
        if event == freevo.PLAY_START:
            if event.arg in self.choices:
                self.select(event.arg)
            # a new item started playing, cache next (if supported)
            if self.next is not None and hasattr(self.next, 'cache'):
                self.next.cache()
            return True
        if not self.selected:
            # There is no selected item. All following functions need
            # with self.selected so pass the event to the parent now.
            if event == freevo.PLAY_END:
                event = freevo.Event(freevo.PLAY_END, self)
            return freevo.MediaItem.eventhandler(self, event)
        if event == freevo.PLAYLIST_TOGGLE_REPEAT:
            self.repeat += 1
            if self.repeat == Playlist.REPEAT_ITEM:
                arg = _('Repeat Item')
            elif self.repeat == Playlist.REPEAT_PLAYLIST:
                arg = _('Repeat Playlist')
            else:
                self.repeat = Playlist.REPEAT_OFF
                arg = _('Repeat Off')
            freevo.OSD_MESSAGE.post(arg)
            return True
        if event == freevo.PLAY_END and event.arg and event.arg in self.choices:
            if self.repeat == Playlist.REPEAT_ITEM:
                # Repeat current item
                self.selected.play()
                return True
            if self.next is not None:
                # Play next item
                self._play_next()
                return True
            # Nothing to play
            self.selected = None
            freevo.PLAY_END.post(self)
            return True
        if event == freevo.PLAYLIST_NEXT:
            if self.next is not None:
                # Stop current item, the next one will start when the
                # current one sends the stop event
                self.selected.stop()
                return True
            # No next item
            freevo.OSD_MESSAGE.post(_('No Next Item In Playlist'))
        if event == freevo.PLAYLIST_PREV:
            if self.selected_pos:
                # This is not the first item. Set next item to previous
                # one and stop the current item
                self.next = self.choices[self.selected_pos - 1]
                self.selected.stop()
                return True
            # No previous item
            freevo.OSD_MESSAGE.post(_('no previous item in playlist'))
        if event == freevo.STOP:
            # Stop playing and send event to parent item
            self.stop()
        # give the event to the next eventhandler in the list
        return freevo.MediaItem.eventhandler(self, event)


class PluginInterface(freevo.MediaPlugin):
    """
    Plugin class for playlist items
    """

    @property
    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return freevo.config.playlist.suffix

    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []
        # get media_type from parent
        media_type = getattr(parent, 'media_type', None)
        for suffix in self.suffix:
            for filename in listing.get(suffix):
                items.append(Playlist(playlist=filename.filename, parent=parent, type=media_type))
        return items


# load the MediaPlugin
interface = PluginInterface()
freevo.activate_plugin(interface)
