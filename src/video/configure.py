#if 0 /*
# -----------------------------------------------------------------------
# configure.py - Configure video playing
# -----------------------------------------------------------------------
# $Id$
#
# Notes: Not integrated right now
# Todo:  Fix some stuff, wait for the mplayer people what they are doing
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/11/24 13:58:45  dischi
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

# The menu widget class
import menu

# The mplayer class
import mplayer

# XML support
import movie_xml

# RegExp
import re

from datatypes import *

menuw = menu.get_singleton()

class MplayerMovieInfo:
    def __init__(self):
        self.time = ""
        self.audio = []
        self.subtitles = []
        self.chapters = 1
        self.audio_selected = None
        self.subtitle_selected = None

        self.re_audio = re.compile("^\[open\] audio stream: [0-9] audio format:"+\
                                   "(.*)aid: ([0-9]*)").match
        self.re_subtitle = re.compile("^\[open\] subtitle.*: ([0-9]) language: "+\
                                      "([a-z][a-z])").match
        self.re_chapter = re.compile("^There are ([0-9]*) chapters in this DVD title.").match
    
    def parse(self, str):
        m = self.re_audio(str)
        if m:
            self.audio += [ (m.group(2), m.group(1)) ]
        m = self.re_subtitle(str)
        if m:
            self.subtitles += [ (m.group(1), m.group(2)) ]
        m = self.re_chapter(str)
        if m:
            self.chapters = int(m.group(1))

    def to_string(self):
        ret = ""
        if self.audio_selected:
            ret += " -aid %s" % self.audio_selected
        if self.subtitle_selected:
            ret += " -sid %s" % self.subtitle_selected
        return ret

#
# Dummy for playing the movie
#

def play_movie(arg=None, menuw=None):
    (mode, file, playlist, repeat, one_time_options, start_time, mpinfo) = arg
    if not isinstance(file, FileInformation):
        file = FileInformation(mode, file)
    file.mplayer_options[1] = mpinfo
    file.mplayer_options[2] = one_time_options
    menuw.delete_menu()
    mplayer.get_singleton().play(mode, file, playlist, repeat, start_time)



#
# Audio menu and selection
#

def audio_selection(arg=None, menuw=None):
    (mpinfo, language) = arg
    mpinfo.audio_selected = language
    menuw.back_one_menu()

def audio_selection_menu(arg=None, menuw=None):
    items = []
    mpinfo = arg
    for a in mpinfo.audio:
        items += [ menu.MenuItem(a[1], audio_selection, (mpinfo, a[0])) ]
    moviemenu = menu.Menu('AUDIO MENU', items)
    menuw.pushmenu(moviemenu)
        

#
# Subtitle menu and selection
#

def subtitle_selection(arg=None, menuw=None):
    (mpinfo, language) = arg
    mpinfo.subtitle_selected = language
    menuw.back_one_menu()

def subtitle_selection_menu(arg=None, menuw=None):
    items = []
    mpinfo = arg
    items += [ menu.MenuItem("no subtitles", subtitle_selection, (mpinfo, None)) ]
    for s in mpinfo.subtitles:
        items += [ menu.MenuItem(s[1], subtitle_selection, (mpinfo, s[0])) ]
    moviemenu = menu.Menu('SUBTITLE MENU', items)
    menuw.pushmenu(moviemenu)

        
#
# Chapter selection
#

def chapter_selection_menu(arg=None, menuw=None):
    items = []
    (mode, file, playlist, repeat, repeat, mpinfo) = arg
    for c in range(1, mpinfo.chapters+1):
        items += [ menu.MenuItem("play chapter %s" % c, play_movie,
                                 (mode, file, playlist, repeat,
                                  '-chapter %s' % c, 0, mpinfo)) ]
    moviemenu = menu.Menu('CHAPTER MENU', items)
    menuw.pushmenu(moviemenu)

#
# config main menu
#

def config_main_menu(mode, file, playlist, repeat, mpinfo):
    next_start = 0
    items = []

    if mpinfo.audio:
        items += [ menu.MenuItem("Audio selection", audio_selection_menu, mpinfo) ]
        
    if mpinfo.subtitles:
        items += [ menu.MenuItem("Subtitle selection", subtitle_selection_menu, mpinfo) ]
        
    if mpinfo.chapters > 1:
        items += [ menu.MenuItem("Chapter selection", chapter_selection_menu,
                                 (mode, file, playlist, repeat, 0, mpinfo)) ]
        
    if mpinfo.time:
        print mpinfo.time
        m = re.compile("^A[: -]*([0-9]+)\.").match(mpinfo.time)
        if m:
            next_start = max(0, int(m.group(1)) - 1)
    if next_start:
        # XXX continue doesn't work good. We save the position where we stopped
        # XXX mplayer, but -ss seems to start on the next i-frame or so :-(
        items += [ menu.MenuItem("play: continue", play_movie,
                                 (mode, file, playlist, repeat, '', next_start, mpinfo)) ]
        
        items += [ menu.MenuItem("play: restart", play_movie,
                                 (mode, file, playlist, repeat, '', 0, mpinfo)) ]
    else:
        items += [ menu.MenuItem("play", play_movie,
                                 (mode, file, playlist, repeat, '', 0, mpinfo)) ]
        
    moviemenu = menu.Menu('CONFIG MENU', items)
    menuw.pushmenu(moviemenu)
    
