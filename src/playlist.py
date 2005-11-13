# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# playlist.py - This is the Freevo playlist reading module.
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: o fix MEMCHECKER comments
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
import random
import os
import re
import copy
import logging

# freevo imports
import config
import util
import plugin
import mediadb
import fxditem

from event import *
from menu import Action, Item, MediaItem, Menu
from gui.windows import ProgressBox

# get logging object
log = logging.getLogger()


REPEAT_OFF      = 0
REPEAT_ITEM     = 1
REPEAT_PLAYLIST = 2

class Playlist(MediaItem):
    """
    Class for playlists. A playlist can be created with a list of items or a
    filename containing the playlist.
    """
    def __init__(self, name='', playlist=[], parent=None, display_type=None,
                 random=False, build=False, autoplay=False, repeat=REPEAT_OFF):
        """
        Init the playlist

        playlist: a) a filename to a playlist file (e.g. m3u)
                  b) a list of items to play, this list can include
                     1) Items
                     2) filenames
                     3) a list (directoryname, recursive=0|1)
        build:    create the playlist. This means unfold the directories
        """
        MediaItem.__init__(self, parent, type='playlist')
        self.name     = Unicode(name)

        # variables only for Playlist
        self.__current = None
        self.__next    = None
        self.playlist     = playlist
        self.autoplay     = autoplay
        self.repeat       = repeat
        self.display_type = display_type

        self.suffixlist   = []
        self.get_plugins  = []

        self.background_playlist = None
        self.random = random

        if build:
            self.build()
        else:
            # create a basic info object
            self.info = mediadb.item()


    def read_m3u(self, plsname):
        """
        This is the (m3u) playlist reading function.

        Arguments: plsname  - the playlist filename
        Returns:   The list of interesting lines in the playlist
        """
        try:
            lines = util.readfile(plsname)
        except IOError:
            log.error('Cannot open file "%s"' % plsname)
            return 0

        try:
            playlist_lines_dos = map(lambda l: l.strip(), lines)
            playlist_lines = filter(lambda l: l[0] != '#', playlist_lines_dos)
        except IndexError:
            log.warning('Bad m3u playlist file "%s"' % plsname)
            return 0

        (curdir, playlistname) = os.path.split(plsname)
        for line in playlist_lines:
            if line.endswith('\r\n'):
                line = line.replace('\\', '/') # Fix MSDOS slashes
            if os.path.exists(os.path.join(curdir,line)):
                self.playlist.append(os.path.join(curdir,line))


    def read_pls(self, plsname):
        """
        This is the (pls) playlist reading function.

        Arguments: plsname  - the playlist filename
        Returns:   The list of interesting lines in the playlist
        """
        try:
            lines = util.readfile(plsname)
        except IOError:
            log.error('Cannot open file "%s"' % list)
            return 0

        playlist_lines_dos = map(lambda l: l.strip(), lines)
        playlist_lines = filter(lambda l: l[0:4] == 'File', playlist_lines_dos)

        for line in playlist_lines:
            numchars=line.find("=")+1
            if numchars > 0:
                playlist_lines[playlist_lines.index(line)] = \
                                                line[numchars:]

        (curdir, playlistname) = os.path.split(plsname)
        for line in playlist_lines:
            if line.endswith('\r\n'):
                line = line.replace('\\', '/') # Fix MSDOS slashes
            if os.path.exists(os.path.join(curdir,line)):
                self.playlist.append(os.path.join(curdir,line))



    def read_ssr(self, ssrname):
        """
        This is the (ssr) slideshow reading function.

        Arguments: ssrname - the slideshow filename
        Returns:   The list of interesting lines in the slideshow

        File line format:

            FileName: "image file name"; Caption: "caption text"; Delay: "sec"

        The caption and delay are optional.
        """

        (curdir, playlistname) = os.path.split(ssrname)
        out_lines = []
        try:
            lines = util.readfile(ssrname)
        except IOError:
            log.error( 'Cannot open file "%s"' % list)
            return 0

        playlist_lines_dos = map(lambda l: l.strip(), lines)
        playlist_lines     = filter(lambda l: l[0] != '#', lines)


        """
        Here's where we parse the line.  See the format above.
        TODO:  Make the search case insensitive
        """
        for line in playlist_lines:
            tmp_list = []
            ss_name = re.findall('FileName: \"(.*?)\"', line)
            ss_caption = re.findall('Caption: \"(.*?)\"', line)
            ss_delay = re.findall('Delay: \"(.*?)\"', line)

            if ss_name != []:
                if ss_caption == []:
                    ss_caption += [""]
                if ss_delay == []:
                    ss_delay += [5]

                for p in self.get_plugins:
                    for i in p.get(self, [os.path.join(curdir, ss_name[0])]):
                        if i.type == 'image':
                            i.name     = Unicode(ss_caption[0])
                            i.duration = int(ss_delay[0])
                            self.playlist.append(i)
                            break
        self.autoplay = True


    def build(self):
        """
        Build the playlist. Create a list of items and filenames. This function
        will load the playlist file or expand directories
        """
        if self.suffixlist:
            # we called this function before
            return

        playlist = self.playlist
        self.playlist = []

        for p in plugin.mimetype(self.display_type):
            #if self.display_type in p.display_type:
            # XXX self.display_type seems to be set to None
            # XXX Which prevents the str->Item from occuring
            # XXX This is a short-term fix I guess
            self.suffixlist += p.suffix()
            self.get_plugins.append(p)

        if isinstance(playlist, (str, unicode)):
            self.set_url(playlist)
            if self.info['playlist'] != None:
                log.info('use cached playlist for %s' % playlist)
                self.playlist = self.info['playlist']
            else:
                log.info('create playlist for %s' % playlist)
                # it's a filename with a playlist
                try:
                    f=open(playlist, "r")
                    line = f.readline()
                    f.close
                    if line.find("[playlist]") > -1:
                        self.read_pls(playlist)
                    elif line.find("[Slides]") > -1:
                        self.read_ssr(playlist)
                    else:
                        self.read_m3u(playlist)
                except (OSError, IOError), e:
                    log.error('playlist error: %s' % e)
                # store the playlist for later use
                self.info.store_with_mtime('playlist', self.playlist)
            return

        # self.playlist is a list of Items or strings (filenames)
        # create a basic info object
        self.info = mediadb.item()

        for i in playlist:
            if isinstance(i, Item):
                # Item object, correct parent
                i = copy.copy(i)
                # FIXME: use weakref here
                i.parent = self
                self.playlist.append(i)

            elif isinstance(i, list) or isinstance(i, tuple) and \
                 len(i) == 2 and os.path.isdir(i[0]):
                # (directory, recursive=True|False)
                if i[1]:
                    match_files = util.match_files_recursively
                else:
                    match_files = util.match_files
                self.playlist += match_files(i[0], self.suffixlist)
                # set autoplay to True on such big lists
                self.autoplay = True

            else:
                # filename
                self.playlist.append(i)


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


    def actions(self):
        """
        return the actions for this item: play and browse
        """
        self.build()
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
        self.build()

        files = []
        for item in self.playlist:
            if not isinstance(item, Item):
                files.append(item)

        listing = mediadb.FileListing(files)
        if listing.num_changes > 10:
            text = _('Scanning playlist, be patient...')
            popup = ProgressBox(text, full=listing.num_changes)
            popup.show()
            listing.update(popup.tick)
            popup.destroy()
        elif listing.num_changes:
            listing.update()

        items = []

        for item in self.playlist:
            if not isinstance(item, Item):
                # get a real item
                listing = mediadb.FileListing([item])
                if listing.num_changes:
                    listing.update()
                for p in self.get_plugins:
                    items += p.get(self, listing)
            else:
                # MEMCHECKER: why is this needed? It is deleted by
                # menu/item.py in the delete function but this there
                # a better way to do this?
                # FIXME: use weakref?
                item.parent = self
                items.append(item)

        self.playlist = items

        if self.random:
            self.randomize()

        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        menu = Menu(self.name, self.playlist, item_types = display_type)
        self.pushmenu(menu)


    def random_play(self):
        """
        play the playlist in random order
        """
        Playlist(playlist=self.playlist, parent=self.parent,
                 display_type=self.display_type, random=True,
                 repeat=self.repeat).play()


    def play(self, next=False):
        """
        play the playlist
        """
        if not self.playlist:
            log.warning('empty playlist')
            return False

        if not next:
            # first start
            Playlist.build(self)

            if self.random:
                self.randomize()

            if self.background_playlist:
                self.background_playlist.play()

            if not self.playlist:
                log.warning('empty playlist')
                return False

            self.__current = self.playlist[0]
            # Send a PLAY_START event for ourself
            PLAY_START.post(self)


        if not isinstance(self.__current, Item):
            # element is a string, make a correct item
            play_items = []

            # get a real item
            l = mediadb.FileListing([self.__current])
            if l.num_changes:
                l.update()
            for p in self.get_plugins:
                for i in p.get(self, l):
                    play_items.append(i)

            if play_items:
                pos = self.playlist.index(self.__current)
                self.__current = play_items[0]
                self.playlist[pos] = play_items[0]

        # get next item
        pos = self.playlist.index(self.__current)
        pos = (pos+1) % len(self.playlist)
        if pos or self.repeat == REPEAT_PLAYLIST:
            self.__next = self.playlist[pos]
        else:
            self.__next = None

        if hasattr(self.__current, 'play'):
            # play the item
            self.__current.play()
            return True

        # The item has no play function. It would be possible to just
        # get all actions and select the first one, but this won't be
        # right. Maybe this action opens a menu and nothing more. So
        # it is play or skip.
        if self.__next:
            return Playlist.play(self, True)
        return True


    def stop(self):
        """
        stop playling
        """
        self.__next = None
        if self.background_playlist:
            self.background_playlist.stop()
            self.background_playlist = None
        if self.__current:
            item = self.__current
            self.__current = None
            item.stop()


    def eventhandler(self, event):
        """
        Handle playlist specific events
        """
        if event == PLAY_START and event.arg in self.playlist:
            # a new item started playing, set internal current one
            self.__current = event.arg
            pos = self.playlist.index(self.__current)
            pos = (pos+1) % len(self.playlist)
            if pos or self.repeat == REPEAT_PLAYLIST:
                self.__next = self.playlist[pos]
                # cache next item (imageviewer)
                if hasattr(self.__next, 'cache'):
                    self.__next.cache()
            else:
                self.__next = None
            return True

        # give the event to the next eventhandler in the list
        if not self.__current:
            return MediaItem.eventhandler(self, event)

        # That doesn't belong here! It should be part of the player!!!
        # if event == PLAY_END:
        #     if self.__current and self.__current.type == 'audio':
        #         AUDIO_LOG.post(self.__current.filename)
        #
        # if event in (INPUT_1, INPUT_2, INPUT_3, INPUT_4, INPUT_5) and \
        #        event.arg and self.__current and \
        #        hasattr(self.__current,'type'):
        #     if (self.__current.type == 'audio'):
        #         RATING.post(event.arg, self.__current.filename)

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
                self.__current.play()
            elif self.__next:
                # Play next item
                self.__current = self.__next
                Playlist.play(self, True)
            else:
                # Nothing to play
                self.stop()
                # Send a PLAY_END event for ourself
                PLAY_END.post(self)
            return True


        if event == PLAYLIST_NEXT:
            if self.__next:
                # Stop current item, the next one will start when the
                # current one sends the stop event
                self.__current.stop()
                return True
            else:
                # No next item
                OSD_MESSAGE.post(_('No Next Item In Playlist'))


        if event == PLAYLIST_PREV:
            pos = self.playlist.index(self.__current)
            if pos:
                # This is not the first item. Set next item to previous
                # one and stop the current item
                self.__next = self.playlist[pos-1]
                self.__current.stop()
                return True
            else:
                # No previous item
                OSD_MESSAGE.post(_('no previous item in playlist'))

        if event == STOP:
            # Stop playing and send event to parent item
            self.stop()

        # give the event to the next eventhandler in the list
        return MediaItem.eventhandler(self, event)





class Mimetype(plugin.MimetypePlugin):
    """
    Plugin class for playlist items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)

        # add fxd parser callback
        fxditem.add_parser([], 'playlist', self.fxdhandler)


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return config.PLAYLIST_SUFFIX + config.IMAGE_SSHOW_SUFFIX


    def get(self, parent, listing):
        """
        return a list of items based on the files
        """
        items = []
        if parent and hasattr(parent, 'display_type'):
            display_type = parent.display_type
        else:
            display_type = None

        for filename in listing.match_suffix(self.suffix()):
            items.append(Playlist(playlist=filename.filename, parent=parent,
                                  display_type=display_type, build=True))
        return items


    def fxdhandler(self, fxd, node):
        """
        parse audio specific stuff from fxd files

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
        children = fxd.get_children(node, 'files')
        dirname  = os.path.dirname(fxd.getattr(None, 'filename', ''))
        if children:
            children = children[0].children

        items = []
        for child in children:
            fname  = os.path.join(dirname, fxd.gettext(child))
            if child.name == 'directory':
                items.append((fname, fxd.getattr(child, 'recursive', 0)))

            elif child.name == 'file':
                items.append(fname)

        pl = Playlist('', items, fxd.getattr(None, 'parent', None),
                      display_type=fxd.getattr(None, 'display_type'),
                      build=True, random=fxd.getattr(node, 'random', 0),
                      repeat=fxd.getattr(node, 'repeat', 0))

        pl.name     = fxd.getattr(node, 'title')
        pl.image    = fxd.childcontent(node, 'cover-img')
        if pl.image:
            pl.image = os.path.join(os.path.dirname(fxd.filename), pl.image)

        fxd.parse_info(fxd.get_children(node, 'info', 1), pl)
        fxd.getattr(None, 'items', []).append(pl)


# load the MimetypePlugin
mimetype = Mimetype()
plugin.activate(mimetype)
