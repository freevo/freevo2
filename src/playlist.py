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
# Revision 1.4  2002/12/03 19:15:17  dischi
# Give all menu callback functions the parameter arg
#
# Revision 1.3  2002/11/28 19:56:12  dischi
# Added copy function
#
# Revision 1.2  2002/11/27 20:22:19  dischi
# Fixed some playlist problems. Sometimes the playlist stopped playing
# after one item is finished. By playling a playlist again, it will start
# with the first item again.
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
#
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

import sys
import random
import time, os
import string
import popen2
import fcntl
import select
import struct
import re
import copy
import random
import menu
import util
import config

from item import Item
from audio.audioitem import AudioItem
from video.videoitem import VideoItem
from image.imageitem import ImageItem

import rc
rc = rc.get_singleton()

TRUE  = 1
FALSE = 0


class Playlist(Item):
    def read_m3u(self, plsname):
        """
        This is the (m3u) playlist reading function.

        Arguments: plsname  - the playlist filename
        Returns:   The list of interesting lines in the playlist
        """

        try:
            lines = open(plsname).readlines()
        except IOError:
            print 'Cannot open file "%s"' % list
            return 0

        playlist_lines_dos = map(lambda l: l.strip(), lines)
        playlist_lines     = filter(lambda l: l[0] != '#', playlist_lines_dos)

        (curdir, playlistname) = os.path.split(plsname)
        for line in playlist_lines:
            if util.match_suffix(line, config.SUFFIX_AUDIO_FILES):
                self.playlist += [ AudioItem(os.path.join(curdir, line), self) ]
            elif util.match_suffix(line, config.SUFFIX_MPLAYER_FILES):
                self.playlist += [ VideoItem(os.path.join(curdir, line), self) ]
            


    def read_pls(self, plsname):
        """
        This is the (pls) playlist reading function.

        Arguments: plsname  - the playlist filename
        Returns:   The list of interesting lines in the playlist
        """

        try:
            lines = open(plsname).readlines()
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
            if util.match_suffix(line, config.SUFFIX_AUDIO_FILES):
                self.playlist += [ AudioItem(os.path.join(curdir, line), self) ]
            elif util.match_suffix(line, config.SUFFIX_MPLAYER_FILES):
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
            lines = open(ssrname).readlines()
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

        # variables only for Playlist
        self.current_item = None
        self.playlist = []
        self.autoplay = FALSE

        if isinstance(file, list):      # file is a playlist
            for i in file:
                element = copy.copy(i)
                element.parent = self
                self.playlist += [ element ]
            self.name = 'Playlist'
        else:
            self.name    = os.path.splitext(os.path.basename(file))[0]
        
            (curdir, playlistname) = os.path.split(file)

            f=open(file, "r")
            line = f.readline()
            f.close
            if line.find("[playlist]") > -1:
                self.read_pls(file)
            elif line.find("[Slides]") > -1:
                self.read_ssr(file)
            else:
                self.read_m3u(file)


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
        moviemenu = menu.Menu(self.name, self.playlist)
        menuw.pushmenu(moviemenu)
        
        
    def play(self, arg=None, menuw=None):
        if not self.playlist:
            print 'empty playlist'
            return FALSE
        
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
            return TRUE

        self.current_item.actions()[0][0](menuw)
        

    def cache_next(self):
        pos = self.playlist.index(self.current_item)
        pos = (pos+1) % len(self.playlist)
        if pos and hasattr(self.playlist[pos], 'cache'):
            self.playlist[pos].cache()


    def eventhandler(self, event, menuw=None):
        if (event == rc.DOWN or event == rc.PLAY_END) and self.current_item \
           and self.playlist:
            pos = self.playlist.index(self.current_item)
            pos = (pos+1) % len(self.playlist)

            if pos:
                if hasattr(self.current_item, 'stop'):
                    self.current_item.stop()
                self.current_item = self.playlist[pos]
                self.play(menuw=menuw, arg='next')
                return TRUE

        # end and no next item
        if event == rc.PLAY_END:
            self.current_item = None
            menuwidget = menu.get_singleton()
            menuwidget.refresh()
            return TRUE
            

        if event == rc.UP and self.current_item and self.playlist:
            pos = self.playlist.index(self.current_item)
            if pos:
                if hasattr(self.current_item, 'stop'):
                    self.current_item.stop()
                pos = (pos-1) % len(self.playlist)
                self.current_item = self.playlist[pos]
                self.play(menuw=menuw, arg='next')
                return TRUE

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
