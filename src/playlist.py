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
                # XXX add display_type
                for p in plugin.mimetype(None):
                    for i in p.get(self, [os.path.join(curdir, line)]):
                        self.playlist.append(i)
                        break
            

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
            # XXX add display_type
            for p in plugin.mimetype(None):
                for i in p.get(self, [os.path.join(curdir, line)]):
                    self.playlist.append(i)
                    break
            


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

                for p in plugin.mimetype('image'):
                    for i in p.get(self, [os.path.join(curdir, ss_name[0])]):
                        if i.type == 'image':
                            i.name     = ss_caption[0]
                            i.duration = int(ss_delay[0])
                            self.playlist.append(i)
                            break


    def __init__(self, file, parent):
        Item.__init__(self, parent)
        self.type     = 'playlist'
        self.menuw    = None

        # variables only for Playlist
        self.current_item = None
        self.playlist = []
        self.autoplay = False

        if isinstance(file, list):      # file is a playlist
            self.filename = ''
            for i in file:
                element = copy.copy(i)
                element.parent = self
                self.playlist += [ element ]
            self.name = 'Playlist'
        else:
            self.filename = file
            self.name    = os.path.splitext(os.path.basename(file))[0]
        

    def read_playlist(self):
        """
        Read the playlist from file and create the items
        """
        if hasattr(self, 'filename') and self.filename and not self.playlist:
            f=open(self.filename, "r")
            line = f.readline()
            f.close
            if line.find("[playlist]") > -1:
                self.read_pls(self.filename)
            elif line.find("[Slides]") > -1:
                self.read_ssr(self.filename)
            else:
                self.read_m3u(self.filename)
        

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
        self.name = _('Random Playlist')

        
    def actions(self):
        """
        return the actions for this item: play and browse
        """
        if self.autoplay:
            return [ ( self.play, _('Play') ),
                     ( self.browse, _('Browse Playlist') ) ]

        return [ ( self.browse, _('Browse Playlist') ),
                 ( self.play, _('Play') ) ]


    def browse(self, arg=None, menuw=None):
        """
        show the playlist in the menu
        """
        self.read_playlist()
        moviemenu = menu.Menu(self.name, self.playlist)
        menuw.pushmenu(moviemenu)
        
        
    def play(self, arg=None, menuw=None):
        """
        play the playlist
        """
        self.read_playlist()
        if not self.menuw:
            self.menuw = menuw

        if not self.playlist:
            # XXX PopupBox please
            print _('empty playlist')
            return False
        
        if not arg or arg != 'next':
            self.current_item = self.playlist[0]
            
        if not self.current_item.actions():
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

            if pos:
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





class RandomPlaylist(Playlist):
    """
    A playlist that can be played in random mode, recursive in subdirs
    or a combination of both. It is _not_ possible to browse this playlist
    right now, only play it.
    """
    def __init__(self, name, playlist, parent, recursive = True,
                 random = True):
        Item.__init__(self, parent)
        self.type         = 'playlist'
        self.name         = name
        
        # variables only for Playlist
        self.current_item = None
        self.playlist     = []
        self.autoplay     = True
        self.unplayed     = playlist
        self.recursive    = recursive
        self.random       = random
        
    def actions(self):
        return [ ( self.play, _('Play') ) ]


    def play_next(self, arg=None, menuw=None):
        if not self.unplayed:
            return False
        
        if self.random:
            element = random.choice(self.unplayed)
        else:
            element = self.unplayed[0]
        self.unplayed.remove(element)

        if not callable(element):
            # element is a string, make a correct item
            files = [ element, ]
            play_items = []

            # get a real item
            for p in plugin.mimetype(None):
                for i in p.get(self, files):
                    play_items.append(i)

            if not play_items:
                return False
                
            element = play_items[0]
                
        self.playlist += [ element ]
        self.current_item = element
        element.parent = self
        element(menuw=menuw)
        return True
        

    def play(self, arg=None, menuw=None):
        if not self.menuw:
            self.menuw = menuw

        if isinstance(self.unplayed, tuple):
            # playlist is a list: dir:prefix
            # build a correct playlist now
            dir, prefix = self.unplayed
            if self.recursive:
                self.unplayed = util.match_files_recursively(dir, prefix)
            else:
                self.unplayed = util.match_files(dir, prefix)

        # reset playlist
        self.unplayed += self.playlist
        self.playlist = []

        # play
        if self.unplayed:
            return self.play_next(arg=arg, menuw=menuw)
        return False


    def cache_next(self):
        pass


    def eventhandler(self, event, menuw=None):
        if not menuw:
            menuw = self.menuw

        if (event == PLAYLIST_NEXT or event == PLAY_END) and self.unplayed:
            if self.current_item:
                self.current_item.parent = self.parent
                if hasattr(self.current_item, 'stop'):
                    try:
                        self.current_item.stop()
                    except OSError:
                        _debug_('ignore playlist event', 1)
                        return True
            return self.play_next(menuw=menuw)

        if event == PLAYLIST_NEXT and not self.unplayed:
            rc.post_event(Event(OSD_MESSAGE, arg=_('no next item in playlist')))
            return True
        
        # end and no next item
        if event in (STOP, PLAY_END, USER_END) and menuw:
            if self.current_item:
                self.current_item.parent = self.parent
            self.current_item = None
            if menuw:
                if hasattr(menuw.menustack[-1], 'is_submenu'):
                    menuw.back_one_menu()
                if menuw.visible:
                    menuw.refresh()
                else:
                    menuw.show()
            return True
            
        if event == PLAYLIST_PREV:
            print 'random playlist up: not implemented yet'

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
    


class Mimetype(plugin.MimetypePlugin):
    """
    Plugin class for playlist items
    """
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
            items.append(Playlist(filename, parent))
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


# load the MimetypePlugin
plugin.activate(Mimetype())

