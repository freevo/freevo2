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
import config
import util
import plugin
import fxditem

from event import *
from menu import Action, Item, MediaItem, Menu, MediaPlugin

# get logging object
log = logging.getLogger()


REPEAT_OFF      = 0
REPEAT_ITEM     = 1
REPEAT_PLAYLIST = 2

class Playlist(MediaItem):
    """
    Class for playlists. A playlist can be created with a list of items, a
    filename containing the playlist or a (list of) beacon query(s).
    """
    def __init__(self, name='', playlist=[], parent=None, type=None,
                 random=False, autoplay=False, repeat=REPEAT_OFF):
        """
        Init the playlist

        playlist: a) a filename to a playlist file (e.g. m3u)
                  b) a list of items to play, this list can include
                     1) Items
                     2) filenames
                     3) a list (directoryname, recursive=0|1)
        """
        MediaItem.__init__(self, parent, type='playlist')
        self.name = str_to_unicode(name)

        # variables only for Playlist
        self.playlist     = playlist
        self.autoplay     = autoplay
        self.repeat       = repeat
        self.display_type = type
        self.next_pos     = None
        self.__playlist_valid = False

        self.background_playlist = None
        self.random = random

        # Listing stuff, this makes it look like a Menu to the listing
        # widget. That needs to be cleaned up, e.g. make a List class and
        # let the listing widget check for it.
        self.state    = 0
        self.selected = None
        self.selected_pos = None

        # create a basic info object
        self.info = {}


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


    def __create_playlist_items(self):
        """
        Build the playlist. Create a list of items and filenames. This function
        will load the playlist file or expand directories
        """
        if self.__playlist_valid:
            # we called this function before
            return
        self.__playlist_valid = True

        # create a basic info object
        self.info = {}
        playlist = self.playlist
        self.playlist = []

        if isinstance(playlist, (str, unicode)):
            # playlist is a filename, load the file and create playlist
            self.set_url(playlist)
            log.info('create playlist for %s' % playlist)
            try:
                f=open(playlist, "r")
                content = map(lambda l: l.strip(' \n\r'), f.readlines())
                f.close
                if content and content[0].find("[playlist]") > -1:
                    playlist = self._read_pls(playlist, content)
                else:
                    playlist = self._read_m3u(playlist, content)
            except (OSError, IOError), e:
                log.error('playlist error: %s' % e)
                playlist = []

        if isinstance(playlist, kaa.beacon.Query):
            playlist = [ playlist ]

        # Note: playlist is a list of Items, strings (filenames) or a
        # beacon queries now.

        plugins = MediaPlugin.plugins(self.display_type)
        for item in playlist:

            if isinstance(item, Item):
                # Item object, correct parent
                item = copy.copy(item)
                item.parent = weakref(self)
                self.playlist.append(item)
                continue

            if not isinstance(item, kaa.beacon.Query):
                # make item a beacon query
                item = kaa.beacon.query(filename=item)

            _playlist = []
            items = item.get(filter='extmap')
            for p in plugins:
                _playlist.extend(p.get(self, items))

            # sort beacon query on url
            _playlist.sort(lambda x,y: cmp(x.url, y.url))
            # add to playlist
            self.playlist.extend(_playlist)


    def randomize(self):
        """
        resort the playlist by random
        """
        old = self.playlist
        self.playlist = []
        while old:
            element = random.choice(old)
            old.remove(element)
            self.playlist += [ element ]


    def __getitem__(self, attr):
        """
        return the specific attribute
        """
        if not self.__playlist_valid:
            self.__create_playlist_items()
        return MediaItem.__getitem__(self, attr)


    def actions(self):
        """
        return the actions for this item: play and browse
        """
        if not self.__playlist_valid:
            self.__create_playlist_items()

        browse = Action(_('Browse Playlist'), self.browse)
        play = Action(_('Play'), self.play)

        if self.autoplay:
            items = [ play, browse ]
        else:
            items = [ browse, play ]

        if not self.random:
            items.append(Action(_('Random play all items'), self.random_play))

        return items


    def browse(self):
        """
        show the playlist in the menu
        """
        if not self.__playlist_valid:
            self.__create_playlist_items()
        if self.random:
            self.randomize()

        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        menu = Menu(self.name, self.playlist, type = display_type)
        self.pushmenu(menu)


    def random_play(self):
        """
        play the playlist in random order
        """
        Playlist(playlist=self.playlist, parent=self.parent,
                 type=self.display_type, random=True,
                 repeat=self.repeat).play()


    def play(self):
        """
        play the playlist
        """
        if not self.playlist:
            log.warning('empty playlist')
            return False

        # First start playing. This is a bad hack and needs to
        # be fixed when fixing the whole self.playlist stuff

        if not self.__playlist_valid:
            self.__create_playlist_items()

        if self.random:
            self.randomize()

        if self.background_playlist:
            self.background_playlist.play()

        if not self.playlist:
            log.warning('empty playlist')
            return False

        # XXX looks like a menu now
        self.choices = self.playlist

        # FIXME: add random code
        self.next_pos = 0
        self.state += 1

        # Send a PLAY_START event for ourself
        PLAY_START.post(self)
        self._play_next()


    def _play_next(self):
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
        if not self.playlist:
            # no need to change stuff (video dir playing)
            return True

        if not hasattr(self, 'choices') or self.choices != self.playlist:
            self.choices = self.playlist
            self.state += 1

        if self.selected == item:
            return True

        self.selected_pos = self.choices.index(item)
        self.selected = item

        if item.menu and item in item.menu.choices:
            # update menu
            item.menu.select(item)

        # get next item
        self.next_pos = (self.selected_pos+1) % len(self.choices)
        if self.next_pos == 0 and not self.repeat == REPEAT_PLAYLIST:
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
        if event == PLAY_START and event.arg in self.playlist:
            # FIXME: remove this after application update
            self.select(event.arg)
            # a new item started playing, cache next (if supported)
            if self.next_pos is not None and \
                   hasattr(self.choices[self.next_pos], 'cache'):
                self.choices[self.next_pos].cache()
            return True

        # give the event to the next eventhandler in the list
        if not self.selected:
            if event == PLAY_END:
                event = Event(PLAY_END, self)
            return MediaItem.eventhandler(self, event)


        if event == PLAYLIST_TOGGLE_REPEAT:
            self.repeat += 1
            if self.repeat == REPEAT_ITEM:
                arg = _('Repeat Item')
            elif self.repeat == REPEAT_PLAYLIST:
                arg = _('Repeat Playlist')
            else:
                self.repeat = REPEAT_OFF
                arg = _('Repeat Off')
            OSD_MESSAGE.post(arg)
            return True


        if event == PLAY_END:
            if self.repeat == REPEAT_ITEM:
                # Repeat current item
                self.selected.play()
                return True
            if self.next_pos is not None:
                # Play next item
                self._play_next()
            else:
                # Nothing to play
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
            else:
                # No next item
                OSD_MESSAGE.post(_('No Next Item In Playlist'))


        if event == PLAYLIST_PREV:
            if self.selected_pos:
                # This is not the first item. Set next item to previous
                # one and stop the current item
                self.next_pos = self.selected_pos - 1
                self.selected.stop()
                return True
            else:
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
        return config.PLAYLIST_SUFFIX


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
