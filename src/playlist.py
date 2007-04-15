# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# playlist.py - This is the Freevo playlist reading module.
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
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

# python imports
import random
import os
import re
import copy
import logging

# kaa imports
import kaa.beacon
from kaa.strutils import str_to_unicode, unicode_to_str
from kaa.weakref import weakref

# freevo imports
from freevo import plugin
from freevo.ui import config
import fxditem

from event import *
from menu import Action, Item, MediaItem, Menu, MediaPlugin, ItemList

# get logging object
log = logging.getLogger()

class Playlist(MediaItem, ItemList):
    """
    Class for playlists. A playlist can be created with a list of items, a
    filename containing the playlist or a (list of) beacon query(s).
    """

    REPEAT_OFF      = 0
    REPEAT_ITEM     = 1
    REPEAT_PLAYLIST = 2

    type = 'playlist'
    
    def __init__(self, name='', playlist=[], parent=None, type=type,
                 random=False, autoplay=False, repeat=REPEAT_OFF):
        """
        Init the playlist

        playlist: a) a filename to a playlist file (e.g. m3u)
                  b) a list of items to play, this list can include
                     1) Items
                     2) filenames
                     3) a list (directoryname, recursive=0|1)
        """
        MediaItem.__init__(self, parent)
        ItemList.__init__(self)

        self.name = str_to_unicode(name)

        # variables only for Playlist
        self._playlist    = playlist
        self.autoplay     = autoplay
        self.repeat       = repeat
        self.display_type = type
        self.next_pos     = None
        # if playlist is empty (like for directory items) the playlist
        # is always valid. The inheriting class has to make sure when
        # it calls set_playlist
        self._playlist_valid = playlist == []
        self.background_playlist = None
        self._random = random

        # create a basic info object
        self.info = {}


    def set_playlist(self, playlist):
        """
        Set a new playlist.
        """
        self.set_items(playlist, 0)


    def _read_m3u(self, plsname, content):
        """
        This is the (m3u) playlist reading function.
        """
        pl_lines = [ l for l in content if not l.startswith('#') ]
        curdir = os.path.split(plsname)[0]

        playlist = []
        for line in pl_lines:
            if line.endswith('\r\n'):
                line = line.replace('\\', '/') # Fix MSDOS slashes
            if os.path.exists(os.path.join(curdir,line)):
                playlist.append(os.path.join(curdir,line))
        return playlist


    def _read_pls(self, plsname, content):
        """
        This is the (pls) playlist reading function.

        Arguments: plsname  - the playlist filename
        Returns:   The list of interesting lines in the playlist
        """
        pl_lines = filter(lambda l: l[0:4] == 'File', content)
        for pos, line in enumerate(pl_lines):
            numchars=line.find("=")+1
            if numchars > 0:
                pl_lines[pos] = line[numchars:]
        curdir = os.path.split(plsname)[0]

        playlist = []
        for line in pl_lines:
            if line.endswith('\r\n'):
                line = line.replace('\\', '/') # Fix MSDOS slashes
            if os.path.exists(os.path.join(curdir,line)):
                playlist.append(os.path.join(curdir,line))
        return playlist


    def _playlist_create_items(self):
        """
        Build the playlist. Create a list of items and filenames. This function
        will load the playlist file or expand directories
        """
        self._playlist_valid = True

        # create a basic info object
        items = []

        if isinstance(self._playlist, (str, unicode)):
            # playlist is a filename, load the file and create playlist
            self.set_url(self._playlist)
            log.info('create playlist for %s' % self._playlist)
            try:
                f=open(self._playlist, "r")
                content = map(lambda l: l.strip(' \n\r'), f.readlines())
                f.close
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
        # beacon queries now.

        plugins = MediaPlugin.plugins(self.display_type)
        for item in self._playlist:

            if isinstance(item, Item):
                # Item object, correct parent
                item = copy.copy(item)
                item.parent = weakref(self)
                items.append(item)
                continue

            if not isinstance(item, kaa.beacon.Query):
                # make item a beacon query
                item = kaa.beacon.query(filename=item)

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


    def __getitem__(self, attr):
        """
        return the specific attribute
        """
        if not self._playlist_valid:
            self._playlist_create_items()
        return MediaItem.__getitem__(self, attr)


    def actions(self):
        """
        return the actions for this item: play and browse
        """
        if not self._playlist_valid:
            self._playlist_create_items()

        browse = Action(_('Browse Playlist'), self.browse)
        play = Action(_('Play'), self.play)

        if self.autoplay:
            items = [ play, browse ]
        else:
            items = [ browse, play ]

        if not self._random:
            items.append(Action(_('Random play all items'), self._play_random))

        return items


    def browse(self):
        """
        show the playlist in the menu
        """
        if not self._playlist_valid:
            self._playlist_create_items()

        # randomize if needed
        self._randomize()

        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        menu = Menu(self.name, self.choices, type = display_type)
        self.pushmenu(menu)


    def play(self):
        """
        play the playlist
        """
        if not self._playlist_valid:
            self._playlist_create_items()

        if not self.choices:
            log.warning('empty playlist')
            return False

        # randomize if needed
        self._randomize()

        if self.background_playlist:
            self.background_playlist.play()

        # FIXME: add random code
        self.next_pos = 0

        # Send a PLAY_START event for ourself
        PLAY_START.post(self)
        self._play_next()


    def _play_random(self):
        """
        play the playlist in random order
        """
        Playlist(playlist=self.choices, parent=self.parent,
                 type=self.display_type, random=True,
                 repeat=self.repeat).play()


    def _play_next(self):
        """
        Play the next item (defined by self.next_pos).
        """
        self.select(self.choices[self.next_pos])

        if hasattr(self.selected, 'play'):
            # play the item
            self.selected.play()
            return True

        # The item has no play function. It would be possible to just
        # get all actions and select the first one, but this won't be
        # right. Maybe this action opens a menu and nothing more. So
        # it is play or skip.
        if self.next_pos is not None:
            return self._play_next(self)
        return True


    def stop(self):
        """
        stop playing
        """
        self.next_pos = None
        if self.background_playlist:
            self.background_playlist.stop()
            self.background_playlist = None
        if self.selected:
            item = self.selected
            self.selected = None
            item.stop()


    def select(self, item):
        """
        Select item that is playing right now.
        """
        ItemList.select(self, item)
        if self.selected is None:
            return False

        if self.selected.menu and self.selected in self.selected.menu.choices:
            # update menu
            self.selected.menu.select(self.selected)

        # get next item
        self.next_pos = (self.selected_pos+1) % len(self.choices)
        if self.next_pos == 0 and not self.repeat == Playlist.REPEAT_PLAYLIST:
            self.next_pos = None


    def get_playlist(self):
        """
        Return playlist object.
        """
        return self


    def eventhandler(self, event):
        """
        Handle playlist specific events
        """
        if event == PLAY_START:
            # a new item started playing, cache next (if supported)
            if self.next_pos is not None and \
                   hasattr(self.choices[self.next_pos], 'cache'):
                self.choices[self.next_pos].cache()
            return True

        if not self.selected:
            # There is no selected item. All following functions need
            # with self.selected so pass the event to the parent now.
            if event == PLAY_END:
                event = Event(PLAY_END, self)
            return MediaItem.eventhandler(self, event)

        if event == PLAYLIST_TOGGLE_REPEAT:
            self.repeat += 1
            if self.repeat == Playlist.REPEAT_ITEM:
                arg = _('Repeat Item')
            elif self.repeat == Playlist.REPEAT_PLAYLIST:
                arg = _('Repeat Playlist')
            else:
                self.repeat = Playlist.REPEAT_OFF
                arg = _('Repeat Off')
            OSD_MESSAGE.post(arg)
            return True

        if event == PLAY_END:
            if self.repeat == Playlist.REPEAT_ITEM:
                # Repeat current item
                self.selected.play()
                return True
            if self.next_pos is not None:
                # Play next item
                self._play_next()
                return True
            # Nothing to play
            self.selected = None
            # Call stop() again here. We need that to stop the bg playlist
            # but it is not good because stop() is called from the outside
            # and will result in this PLAY_END.
            self.stop()
            # Send a PLAY_END event for ourself
            PLAY_END.post(self)
            return True

        if event == PLAYLIST_NEXT:
            if self.next_pos is not None:
                # Stop current item, the next one will start when the
                # current one sends the stop event
                self.selected.stop()
                return True
            # No next item
            OSD_MESSAGE.post(_('No Next Item In Playlist'))

        if event == PLAYLIST_PREV:
            if self.selected_pos:
                # This is not the first item. Set next item to previous
                # one and stop the current item
                self.next_pos = self.selected_pos - 1
                self.selected.stop()
                return True
            # No previous item
            OSD_MESSAGE.post(_('no previous item in playlist'))

        if event == STOP:
            # Stop playing and send event to parent item
            self.stop()

        # give the event to the next eventhandler in the list
        return MediaItem.eventhandler(self, event)



class PluginInterface(MediaPlugin):
    """
    Plugin class for playlist items
    """
    def __init__(self):
        MediaPlugin.__init__(self)

        # add fxd parser callback
        fxditem.add_parser([], 'playlist', self.fxdhandler)


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return config.playlist.suffix


    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []
        if parent and hasattr(parent, 'display_type'):
            display_type = parent.display_type
        else:
            display_type = None

        for suffix in self.suffix():
            for filename in listing.get(suffix):
                items.append(Playlist(playlist=filename.filename, parent=parent,
                                      type=display_type))
        return items


    def fxdhandler(self, node, parent, listing):
        """
        parse playlist specific stuff from fxd files

        <?xml version="1.0" ?>
        <freevo>
          <playlist title="foo" random="1|0" repeat="1|0">
            <cover-img>foo.jpg</cover-img>
            <files>
              <directory recursive="1|0">path</directory>
              <file>filename</file>
            </files>
            <info>
              <description>A nice description</description>
            </info>
          </playlist>
        </freevo>
        """
        items = []
        for c in node.children:
            if not c.name == 'files':
                continue
            for file in c.children:
                if file.name in ('file', 'directory'):
                    f = unicode_to_str(file.content)
                    filename = os.path.join(node.dirname, f)
                    query = kaa.beacon.query(filename=filename)
                if file.name == 'directory':
                    recursive = file.getattr('recursive') == '1'
                    query = query.get().list(recursive=recursive)
                items.append(query)

        # create playlist object
        pl = Playlist(node.title, items, parent, parent.display_type,
                      random=node.getattr('random') == '1',
                      repeat=node.getattr('repeat') == '1')
        pl.image = node.image
        pl.info  = node.info
        return pl


# load the MediaPlugin
interface = PluginInterface()
plugin.activate(interface)
