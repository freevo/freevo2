#if 0 /*
# -----------------------------------------------------------------------
# playlist.py - This is the Freevo playlist reading module. 
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.45  2003/12/18 18:19:27  outlyer
# If we're using a playlist file, make sure the object has that attribute
# so we can use fileops on it later.
#
# Revision 1.44  2003/12/18 17:07:52  outlyer
# Two bugfixes for the previously broken playlist stuff:
#
# * Don't iterate over the playlist if it is a string, since it just splits
#     the string into characters
# * self.display_type seems to be set to None, so the playlist.Mimetype plugin
#     is never loaded
#
# Playlists are working again! Woohoo!
#
# TODO:
#     Figure out why display_type is always none; shouldn't it be the menu type
#     or something?
#
# Revision 1.43  2003/12/13 18:16:34  dischi
# allow fxd playlists with relative path
#
# Revision 1.42  2003/12/10 19:51:51  dischi
# make playlist files work again
#
# Revision 1.41  2003/12/08 20:40:57  dischi
# add doc
#
# Revision 1.40  2003/12/08 20:37:33  dischi
# merged Playlist and RandomPlaylist into one class
#
# Revision 1.39  2003/12/08 16:18:44  mikeruelle
# getting a lot of crashes. quickfix
#
# Revision 1.38  2003/12/07 19:11:22  dischi
# o add <playlist> fxd support
# o add background_playlist to a playlist to support playing music
#   in slideshows
#
# Revision 1.37  2003/12/01 19:06:46  dischi
# better handling of the MimetypePlugin
#
# Revision 1.36  2003/11/30 14:41:10  dischi
# use new Mimetype plugin interface
#
# Revision 1.35  2003/11/28 20:08:56  dischi
# renamed some config variables
#
# Revision 1.34  2003/11/28 19:26:36  dischi
# renamed some config variables
#
# Revision 1.33  2003/11/21 11:43:58  dischi
# send event if there is not next playlist event
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
#endif

import random
import os
import re
import copy

import config
import menu
import util
import rc
import plugin

from event import *
from item import Item


class Playlist(Item):

    def __init__(self, name='', playlist=[], parent=None, display_type=None,
                 random=False, build=False, autoplay=False, repeat=False):
        """
        Init the playlist

        playlist: a) a filename to a playlist file (e.g. m3u)
                  b) a list of items to play, this list can include
                     1) Items
                     2) filenames
                     3) a list (directoryname, recursive=0|1)
        build:    create the playlist. This means unfold the directories
        """
        Item.__init__(self, parent)

        self.type     = 'playlist'
        self.menuw    = None
        self.name     = name
        
        if (isinstance(playlist, str) or isinstance(playlist, unicode)) and not name:
            self.name = util.getname(playlist)
            self.filename = playlist            # Needed for fileops
            
        # variables only for Playlist
        self.current_item = None
        self.playlist     = playlist
        self.autoplay     = autoplay
        self.repeat       = repeat
        self.display_type = display_type

        self.__build__    = False
        self.suffixlist   = []
        self.get_plugins  = []

        self.background_playlist = None
        if build:
            self.build()

        self.random = random


    def read_m3u(self, plsname):
        """
        This is the (m3u) playlist reading function.

        Arguments: plsname  - the playlist filename
        Returns:   The list of interesting lines in the playlist
        """
        try:
            lines = util.readfile(plsname)
        except IOError:
            print 'Cannot open file "%s"' % list
            return 0

        playlist_lines_dos = map(lambda l: l.strip(), lines)
        playlist_lines     = filter(lambda l: l[0] != '#', playlist_lines_dos)

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
            print _('Cannot open file "%s"') % list
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
            print _('Cannot open file "%s"') % list
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
                            i.name     = ss_caption[0]
                            i.duration = int(ss_delay[0])
                            self.playlist.append(i)
                            break


    def build(self):
        """
        Build the playlist. Create a list of items and filenames. This function
        will load the playlist file or expand directories
        """
        if self.suffixlist:
            # we called this function before
            return

        playlist      = self.playlist
        self.playlist = []
       
        for p in plugin.mimetype(self.display_type):
            #if self.display_type in p.display_type:
            # XXX self.display_type seems to be set to None
            # XXX Which prevents the str->Item from occuring
            # XXX This is a short-term fix I guess
            self.suffixlist += p.suffix()
            self.get_plugins.append(p)
                
        if isinstance(playlist, str) or isinstance(playlist, unicode):
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
            except OSError, e:
                print 'playlist error: %s' % e


        # self.playlist is a list of Items or strings (filenames)
        if not isinstance(playlist, str):
            for i in playlist:
                if isinstance(i, Item):
                    # Item object, correct parent
                    i = copy.copy(i)
                    i.parent = self
                    self.playlist.append(i)

                elif isinstance(i, list) or isinstance(i, tuple) and \
                     len(i) == 2 and vfs.isdir(i[0]):
                    # (directory, recursive=True|False)
                    if i[1]:
                        self.playlist += util.match_files_recursively(i[0], self.suffixlist)
                    else:
                        self.playlist += util.match_files(i[0], self.suffixlist)
                    # set autoplay to True on such big lists
                    self.autoplay = True

                else:
                    # filename
                    self.playlist.append(i)

        self.__build__ = True
                

    def copy(self, obj):
        """
        Special copy value Playlist
        """
        Item.copy(self, obj)
        if obj.type == 'playlist':
            self.current_item = obj.current_item
            self.playlist     = obj.playlist
            self.autoplay     = obj.autoplay
            

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
        if self.autoplay:
            return [ ( self.play, _('Play') ),
                     ( self.browse, _('Browse Playlist') ) ]

        return [ ( self.browse, _('Browse Playlist') ),
                 ( self.play, _('Play') ) ]


    def browse(self, arg=None, menuw=None):
        """
        show the playlist in the menu
        """
        self.build()
        for item in self.playlist:
            if not callable(item):
                # element is a string, make a correct item
                play_items = []

                # get a real item
                for p in self.get_plugins:
                    for i in p.get(self, [ item ]):
                        play_items.append(i)

                if play_items:
                    pos = self.playlist.index(item)
                    self.playlist[pos] = play_items[0]

        if self.random:
            self.randomize()

        moviemenu = menu.Menu(self.name, self.playlist)
        menuw.pushmenu(moviemenu)
        
        
    def play(self, arg=None, menuw=None):
        """
        play the playlist
        """
        if not self.menuw:
            self.menuw = menuw

        if not self.playlist:
            # XXX PopupBox please
            print _('empty playlist')
            return False
        

        if not arg or arg != 'next':
            # first start
            self.build()
            if self.random:
                self.randomize()

            if self.background_playlist:
                self.background_playlist.play()

            self.current_item = self.playlist[0]


        if not callable(self.current_item):
            # element is a string, make a correct item
            play_items = []

            # get a real item
            for p in self.get_plugins:
                for i in p.get(self, [ self.current_item ]):
                    play_items.append(i)

            if play_items:
                pos = self.playlist.index(self.current_item)
                self.current_item = play_items[0]
                self.playlist[pos] = play_items[0]

            
        if not hasattr(self.current_item, 'actions') or not self.current_item.actions():
            # skip item
            pos = self.playlist.index(self.current_item)
            pos = (pos+1) % len(self.playlist)

            if pos:
                self.current_item = self.playlist[pos]
                self.play(menuw=menuw, arg='next')
            else:
                # no repeat
                self.current_item = None
            return True

        self.current_item.actions()[0][0](menuw=menuw)
        

    def cache_next(self):
        """
        cache next item, usefull for image playlists
        """
        pos = self.playlist.index(self.current_item)
        pos = (pos+1) % len(self.playlist)
        if pos and hasattr(self.playlist[pos], 'cache'):
            self.playlist[pos].cache()


    def stop(self):
        """
        stop playling
        """
        if self.background_playlist:
            self.background_playlist.stop()
        if self.current_item:
            self.current_item.parent = self.parent
            if hasattr(self.current_item, 'stop'):
                try:
                    self.current_item.stop()
                except OSError:
                    pass
        

    def eventhandler(self, event, menuw=None):
        """
        Handle playlist specific events
        """
        if not menuw:
            menuw = self.menuw
            
        if event in ( PLAYLIST_NEXT, PLAY_END, USER_END) \
               and self.current_item and self.playlist:
            pos = self.playlist.index(self.current_item)
            pos = (pos+1) % len(self.playlist)

            if pos or self.repeat:
                if hasattr(self.current_item, 'stop'):
                    try:
                        self.current_item.stop()
                    except OSError:
                        _debug_('ignore playlist event', 1)
                        return True
                self.current_item = self.playlist[pos]
                self.play(menuw=menuw, arg='next')
                return True
            elif event == PLAYLIST_NEXT:
                rc.post_event(Event(OSD_MESSAGE, arg=_('no next item in playlist')))

                
        # end and no next item
        if event in (PLAY_END, USER_END, STOP):
            if self.background_playlist:
                self.background_playlist.stop()
            self.current_item = None
            if menuw:
                menuw.show()
            return True
            

        if event == PLAYLIST_PREV and self.current_item and self.playlist:
            pos = self.playlist.index(self.current_item)
            if pos:
                if hasattr(self.current_item, 'stop'):
                    try:
                        self.current_item.stop()
                    except OSError:
                        _debug_('ignore playlist event', 1)
                        return True
                pos = (pos-1) % len(self.playlist)
                self.current_item = self.playlist[pos]
                self.play(menuw=menuw, arg='next')
                return True
            else:
                rc.post_event(Event(OSD_MESSAGE, arg=_('no previous item in playlist')))

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)


    


class Mimetype(plugin.MimetypePlugin):
    """
    Plugin class for playlist items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)

        # register the callback
        plugin.register_callback('fxditem', [], 'playlist', self.fxdhandler)


    def suffix(self):
        """
        return the list of suffixes this class handles
        """
        return config.PLAYLIST_SUFFIX + config.IMAGE_SSHOW_SUFFIX

    
    def get(self, parent, files):
        """
        return a list of items based on the files
        """
        items = []

        for filename in util.find_matches(files, self.suffix()):
            items.append(Playlist(playlist=filename, parent=parent, build=True))
            files.remove(filename)

        return items


    def update(self, parent, new_files, del_files, new_items, del_items, current_items):
        """
        update a directory. Add items to del_items if they had to be removed based on
        del_files or add them to new_items based on new_files
        """
        for item in current_items:
            # remove 'normal' files
            for file in util.find_matches(del_files, self.suffix()):
                if item.type == 'playlist' and item.filename == file and not \
                   item in del_items:
                    del_items += [ item ]
                    del_files.remove(file)

        # add new 'normal' files
        for file in util.find_matches(new_files, self.suffix()):
            new_items.append(Playlist(file, parent))
            new_files.remove(file)


    def fxdhandler(self, fxd, node):
        """
        parse audio specific stuff from fxd files

        <?xml version="1.0" ?>
        <freevo>
          <playlist title="foo" random="1|0">
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
                      build=True, random=fxd.getattr(node, 'random', 0))

        pl.name     = fxd.getattr(node, 'title')
        pl.xml_file = fxd.getattr(None, 'filename', '')
        pl.image    = fxd.childcontent(node, 'cover-img')
        if pl.image:
            pl.image = vfs.join(vfs.dirname(pl.xml_file), pl.image)

        fxd.parse_info(fxd.get_children(node, 'info', 1), pl)
        fxd.getattr(None, 'items', []).append(pl)


# load the MimetypePlugin
plugin.activate(Mimetype())
