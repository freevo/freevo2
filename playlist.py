# ----------------------------------------------------------------------
# playlist.py - This is the Freevo playlist reading module. 
# ----------------------------------------------------------------------
# $Id$
# ----------------------------------------------------------------------
# $Log$
# Revision 1.5  2002/11/24 13:35:48  dischi
# removed the code cleanup stuff, it will go into the subdir src
#
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
