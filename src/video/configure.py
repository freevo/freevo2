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
# Revision 1.2  2002/11/26 20:58:44  dischi
# o Fixed bug that not only the first character of mplayer_options is used
# o added the configure stuff again (without play from stopped position
#   because the mplayer -ss option is _very_ broken)
# o Various fixes in DVD playpack
#
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

# RegExp
import re

menuw = menu.get_singleton()


#
# Dummy for playing the movie
#

def play_movie(arg=None, menuw=None):
    menuw.delete_menu()
    arg[0].play(menuw=menuw, arg=arg[1])



#
# Audio menu and selection
#

def audio_selection(arg=None, menuw=None):
    arg[0].selected_audio = arg[1]
    menuw.back_one_menu()

def audio_selection_menu(arg=None, menuw=None):
    items = []
    for a in arg.available_audio_tracks:
        items += [ menu.MenuItem(a[1], audio_selection, (arg, a[0])) ]
    moviemenu = menu.Menu('AUDIO MENU', items)
    menuw.pushmenu(moviemenu)
        

#
# Subtitle menu and selection
#

def subtitle_selection(arg=None, menuw=None):
    arg[0].selected_subtitle = arg[1]
    menuw.back_one_menu()

def subtitle_selection_menu(arg=None, menuw=None):
    items = []

    items += [ menu.MenuItem("no subtitles", subtitle_selection, (arg, None)) ]
    for s in arg.available_subtitles:
        items += [ menu.MenuItem(s[1], subtitle_selection, (arg, s[0])) ]
    moviemenu = menu.Menu('SUBTITLE MENU', items)
    menuw.pushmenu(moviemenu)

        
#
# Chapter selection
#

def chapter_selection_menu(arg=None, menuw=None):
    items = []
    for c in range(1, arg.available_chapters+1):
        items += [ menu.MenuItem("play chapter %s" % c, play_movie,
                                 (arg, ' -chapter %s' % c)) ]
    moviemenu = menu.Menu('CHAPTER MENU', items)
    menuw.pushmenu(moviemenu)

#
# config main menu
#

def main_menu(item):
    next_start = 0
    items = []

    if item.available_audio_tracks:
        items += [ menu.MenuItem("Audio selection", audio_selection_menu, item) ]
        
    if item.available_subtitles:
        items += [ menu.MenuItem("Subtitle selection", subtitle_selection_menu, item) ]
        
    if item.available_chapters > 1:
        items += [ menu.MenuItem("Chapter selection", chapter_selection_menu, item) ]
        
    items += [ menu.MenuItem("play", play_movie, (item, '')) ]
        
    moviemenu = menu.Menu('CONFIG MENU', items)
    menuw.pushmenu(moviemenu)
    
