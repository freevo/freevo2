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
# Revision 1.25  2003/09/19 22:07:15  dischi
# TRUE/True/FALSE/False changes
#
# Revision 1.24  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
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
import menu
import util
import config
import event as em

from item import Item

import video
import audio
import image
import games

from audio import AudioItem
from video import VideoItem
from image import ImageItem

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
                # skip files that don't exist
                if util.match_suffix(line, config.SUFFIX_AUDIO_FILES):
                    self.playlist += [ AudioItem(os.path.join(curdir, line), self) ]
                elif util.match_suffix(line, config.SUFFIX_VIDEO_FILES):
                    self.playlist += [ VideoItem(os.path.join(curdir, line), self) ]
            

    def read_pls(self, plsname):
        """
        This is the (pls) playlist reading function.

        Arguments: plsname  - the playlist filename
        Returns:   The list of interesting lines in the playlist
        """

        try:
            lines = util.readfile(plsname)
        except IOError:
            print 'Cannot open file "%s"' % list
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
            if util.match_suffix(line, config.SUFFIX_AUDIO_FILES):
                self.playlist += [ AudioItem(os.path.join(curdir, line), self) ]
            elif util.match_suffix(line, config.SUFFIX_VIDEO_FILES):
                self.playlist += [ VideoItem(os.path.join(curdir, line), self) ]
            


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
            print 'Cannot open file "%s"' % list
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

                self.playlist += [ ImageItem(os.path.join(curdir, ss_name[0]), self,
                                             ss_caption[0], int(ss_delay[0])) ]



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
        self.name = 'Random Playlist'

        
    def actions(self):
        if self.autoplay:
            return [ ( self.play, 'Play' ),
                     ( self.browse, 'Browse Playlist' ) ]

        return [ ( self.browse, 'Browse Playlist' ),
                 ( self.play, 'Play' ) ]


    def browse(self, arg=None, menuw=None):
        self.read_playlist()
        moviemenu = menu.Menu(self.name, self.playlist)
        menuw.pushmenu(moviemenu)
        
        
    def play(self, arg=None, menuw=None):
        self.read_playlist()
        if not self.menuw:
            self.menuw = menuw

        if not self.playlist:
            print 'empty playlist'
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
        pos = self.playlist.index(self.current_item)
        pos = (pos+1) % len(self.playlist)
        if pos and hasattr(self.playlist[pos], 'cache'):
            self.playlist[pos].cache()


    def eventhandler(self, event, menuw=None):
        if not menuw:
            menuw = self.menuw
            
        if event in ( em.PLAYLIST_NEXT, em.PLAY_END, em.USER_END) \
               and self.current_item and self.playlist:
            pos = self.playlist.index(self.current_item)
            pos = (pos+1) % len(self.playlist)

            if pos:
                if hasattr(self.current_item, 'stop'):
                    self.current_item.stop()
                self.current_item = self.playlist[pos]
                self.play(menuw=menuw, arg='next')
                return True

        # end and no next item
        if event in (em.PLAY_END, em.USER_END, em.STOP):
            self.current_item = None
            if menuw:
                menuw.show()
            return True
            

        if event == em.PLAYLIST_PREV and self.current_item and self.playlist:
            pos = self.playlist.index(self.current_item)
            if pos:
                if hasattr(self.current_item, 'stop'):
                    self.current_item.stop()
                pos = (pos-1) % len(self.playlist)
                self.current_item = self.playlist[pos]
                self.play(menuw=menuw, arg='next')
                return True

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)





class RandomPlaylist(Playlist):
    def __init__(self, playlist, parent, add_args = None):
        Item.__init__(self, parent)
        self.type     = 'playlist'

        # variables only for Playlist
        self.current_item = None
        self.playlist = []
        self.autoplay = True
        self.unplayed = playlist

        
    def actions(self):
        return [ ( self.play, 'Play' ) ]


    def play_next(self, arg=None, menuw=None):
        element = random.choice(self.unplayed)
        self.unplayed.remove(element)
        if not callable(element):
            # try to get the item for this file
            files = [ element, ]
            play_items = []
            for t in ( 'video', 'audio', 'image', 'games' ):
                play_items += eval(t + '.cwd(self, files)')

            if not play_items:
                print 'FIXME: this should never happen'
                return False
                
            element = play_items[0]
                
        self.playlist += [ element ]
        self.current_item = element
        element.parent = self
        element(menuw=menuw)
        return True
        

    def play(self, arg=None, menuw=None):
        if isinstance(self.unplayed, tuple):
            dir, prefix = self.unplayed
            self.unplayed = util.match_files_recursively(dir, prefix)

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

        if (event == em.PLAYLIST_NEXT or event == em.PLAY_END) and self.unplayed:
            if self.current_item:
                self.current_item.parent = self.parent
                if hasattr(self.current_item, 'stop'):
                    self.current_item.stop()
            return self.play_next(menuw=menuw)
        
        # end and no next item
        if event == em.PLAY_END:
            if self.current_item:
                self.current_item.parent = self.parent
            self.current_item = None
            if menuw:
                menuw.show()
            return True
            
        if event == em.PLAYLIST_PREV:
            print 'random playlist up: not implemented yet'

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
    
