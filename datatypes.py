#if 0
# -----------------------------------------------------------------------
# datatypes.py - Some datatypes we need all the time
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2002/11/09 17:33:13  dischi
# Small change in the mplayer_options
#
# Revision 1.4  2002/11/08 21:28:20  dischi
# Added support for a movie config dialog. Only usable for dvd right now.
# See mplayer-devel list for details.
#
# Revision 1.3  2002/10/10 09:27:30  dischi
# added runtime to MovieExtraInformation
#
# Revision 1.2  2002/10/08 15:50:54  dischi
# Parse more infos from the xml file to MovieExtraInformation (maybe we
# should change that name...)
#
# Revision 1.1  2002/10/06 14:58:51  dischi
# Lots of changes:
# o removed some old cvs log messages
# o some classes without member functions are in datatypes.py
# o movie_xml.parse now returns an object of MovieInformation instead of
#   a long list
# o mplayer_options now works better for options on cd/dvd/vcd
# o you can disable -wid usage
# o mplayer can play movies as strings or as FileInformation objects with
#   mplayer_options
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
# -----------------------------------------------------------------------
#endif


class RemovableMediaInfo:
    def __init__(self, type, label = None, image = None, play_options = None, \
                 info = None):
        self.type = type
        self.label = label
        self.image = image
        self.play_options = play_options
        self.info = info


class FileInformation:
    def __init__(self, mode='video', file=None, mplayer_options=''):
        self.mode = mode
        self.file = file

        # mplayer options is a triple:
        # 1. settings for this file, e.g. from xml
        # 2. settings from parsing prev. mplayer calls for this file
        # 3. settings only for the next mplayer start (e.g. -ss, -chapter)
        self.mplayer_options = [ mplayer_options, None, '' ]
        self.mplayer_config = ""

class MovieInformation:
    def __init__(self, title=None, image=None, playlist=None, disc_id=None, \
                 disc_label=None, info=None, xml_file = ''):
        self.title = title
        self.image = image
        self.playlist = playlist
        self.disc_id = disc_id
        self.disc_label = disc_label
        self.info = info
        self.xml_file = xml_file

class MovieExtraInformation:
    def __init__(self):
        self.url = self.genre = self.tagline = self.plot = ''
        self.runtime = self.year = self.rating = ''
        
