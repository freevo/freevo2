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
        self.mplayer_options = mplayer_options


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
