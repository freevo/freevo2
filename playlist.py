# ----------------------------------------------------------------------
# playlist.py - This is the Freevo playlist reading module. 
# ----------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------
# $Log$
# Revision 1.4  2002/11/23 19:32:06  dischi
# Some stuff needed by the code cleanup, shouldn't break anything
#
# Revision 1.3  2002/11/15 02:11:38  krister
# Applied Bob Pauwes latest image slideshow patches.
#
# Revision 1.2  2002/11/14 04:38:47  krister
# Added Bob Pauwe's image slideshow patches.
#
# Revision 1.1  2002/10/31 21:11:02  dischi
# playlist parser, returns a list of all files. There a separat functions
# for the different types of playlists. Feel free to add more
#
#
# ----------------------------------------------------------------------
#
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
# ----------------------------------------------------------------------


import sys
import random
import time, os
import string
import popen2
import fcntl
import select
import struct
import re


def read_m3u(plsname):
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

    return playlist_lines

def read_pls(plsname):
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

    return playlist_lines

def read_ssr(ssrname):
    """
    This is the (ssr) slideshow reading function.

    Arguments: ssrname - the slideshow filename
    Returns:   The list of interesting lines in the slideshow

    File line format:

      FileName: "image file name"; Caption: "caption text"; Delay: "sec"

    The caption and delay are optional.
    """

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
            tmp_list.append(ss_name[0])
            tmp_list.append(ss_caption[0])
            tmp_list.append(int(ss_delay[0]))
            out_lines.append(tmp_list)

    return out_lines


def read_playlist(playlist_file, start_playing=0):
    """
    This is the (m3u/pls) playlist handling function.

    Arguments: arg[0]  - the playlist filename
    Returns:   Boolean
    """
    (curdir, playlistname) = os.path.split(playlist_file)

    f=open(playlist_file, "r")
    line = f.readline()
    f.close
    if line.find("[playlist]") > -1:
        playlist_lines = read_pls(playlist_file)
        pl_type = 1
    elif line.find("[Slides]") > -1:
        playlist_lines = read_ssr(playlist_file)
        pl_type = 3
    else:
        playlist_lines = read_m3u(playlist_file)
        pl_type = 1
                
    if start_playing and len(playlist_lines):
        play(arg=('audio', playlist_lines[0], playlist_lines))
        return 0

    items = []
    for line in playlist_lines:
        # Standard playlist format, 1 filename per line
        if pl_type == 1:
            if line.rfind("://") == -1:
                # it seems a file
                (dirname, filename) = os.path.split(line)

                # that doesn't have a path or is absolute
                if not dirname: 
                    dirname = curdir

                playlist_lines[playlist_lines.index(line)] = \
                      os.path.join(os.path.abspath(dirname), filename) 

        # Enhanced playlist format, an array of items per line, the first
        # is the filename.
        elif pl_type == 3:
            # is it a URL?
            if line[0].rfind("://") == -1:
                # it seems a file
                (dirname, filename) = os.path.split(line[0])

                # that doesn't have a path or is absolute
                if not dirname: 
                    dirname = curdir

                # I think we need to prepend curdir to dirname if
                # dirname isn't absolute!
                if dirname[0] != '/':
                    dirname = curdir + '/' + dirname

                playlist_lines[playlist_lines.index(line)][0] = \
                      os.path.join(os.path.abspath(dirname), filename)

    return playlist_lines

















from item import Item
import rc
rc = rc.get_singleton()

TRUE  = 1
FALSE = 0



class Playlist(Item):
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
        Item.__init__(self)
        self.type     = 'playlist'
        self.current_item = None
        self.parent = parent

        self.name    = os.path.splitext(os.path.basename(file))[0]
        self.playlist = []
        self.autoplay = FALSE
        
        (curdir, playlistname) = os.path.split(file)

        f=open(file, "r")
        line = f.readline()
        f.close
        if line.find("[playlist]") > -1:
            pass
        elif line.find("[Slides]") > -1:
            self.read_ssr(file)


    def actions(self):
        if self.autoplay:
            return [ ( self.play, 'Play' ),
                     ( self.browse, 'Browse Playlist' ) ]

        return [ ( self.browse, 'Browse Playlist' ),
                 ( self.play, 'Play' ) ]


    def browse(self, menuw=None):
        moviemenu = menu.Menu(self.name, self.playlist)
        menuw.pushmenu(moviemenu)
        
        
    def play(self, menuw=None):
        if not self.playlist:
            print 'empty playlist'

        if not self.current_item:
            self.current_item = self.playlist[0]
            
        if not self.current_item.actions():
            # skip item
            pos = self.playlist.index(self.current_item)
            pos = (pos+1) % len(self.playlist)

            if pos:
                self.current_item = self.playlist[pos]
                self.play(menuw)
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
                self.play(menuw)
            return TRUE

        if event == rc.UP and self.current_item and self.playlist:
            pos = self.playlist.index(self.current_item)
            if pos:
                if hasattr(self.current_item, 'stop'):
                    self.current_item.stop()
                pos = (pos-1) % len(self.playlist)
                self.current_item = self.playlist[pos]
                self.play(menuw)
            return TRUE

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
