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
# Revision 1.8  2003/03/31 20:44:52  dischi
# shorten time between pop.destroy and menu drawing
#
# Revision 1.7  2003/03/30 16:50:20  dischi
# pass xml_file definition to submenus
#
# Revision 1.6  2003/03/02 14:58:23  dischi
# Removed osd.clearscreen and if we have the NEW_SKIN deactivate
# skin.popupbox, refresh, etc. Use menuw.show and menuw.hide to do this.
#
# Revision 1.5  2003/01/07 19:45:17  dischi
# small bugfix
#
# Revision 1.4  2002/12/22 12:23:30  dischi
# Added deinterlacing in the config menu
#
# Revision 1.3  2002/11/26 21:42:28  dischi
# small bugfix to remove configure menu for chapters
#
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


current_xml_file = None

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
    global current_xml_file
    items = []
    for a in arg.available_audio_tracks:
        items += [ menu.MenuItem(a[1], audio_selection, (arg, a[0])) ]
    moviemenu = menu.Menu('AUDIO MENU', items, xml_file=current_xml_file)
    menuw.pushmenu(moviemenu)
        

#
# Subtitle menu and selection
#

def subtitle_selection(arg=None, menuw=None):
    arg[0].selected_subtitle = arg[1]
    menuw.back_one_menu()

def subtitle_selection_menu(arg=None, menuw=None):
    global current_xml_file
    items = []

    items += [ menu.MenuItem("no subtitles", subtitle_selection, (arg, None)) ]
    for s in arg.available_subtitles:
        items += [ menu.MenuItem(s[1], subtitle_selection, (arg, s[0])) ]
    moviemenu = menu.Menu('SUBTITLE MENU', items, xml_file=current_xml_file)
    menuw.pushmenu(moviemenu)

        
#
# Chapter selection
#

def chapter_selection(menuw=None, arg=None):
    menuw.delete_menu()
    play_movie(menuw=menuw, arg=arg)
    
def chapter_selection_menu(arg=None, menuw=None):
    global current_xml_file
    items = []
    for c in range(1, arg.available_chapters+1):
        items += [ menu.MenuItem("play chapter %s" % c, chapter_selection,
                                 (arg, ' -chapter %s' % c)) ]
    moviemenu = menu.Menu('CHAPTER MENU', items, xml_file=current_xml_file)
    menuw.pushmenu(moviemenu)


#
# De-interlacer
#

def toggle(arg=None, menuw=None):
    setattr(arg[0], arg[1], not getattr(arg[0], arg[1]))

    sel = menuw.all_items.index(menuw.menustack[-1].selected)

    menuw.menustack[-1].choices = main_menu_generate(arg[0])
    menuw.menustack[-1].selected = menuw.menustack[-1].choices[sel]

    menuw.init_page()
    menuw.refresh()


def add_toogle(name, item, var):
    if getattr(item, var):
        return menu.MenuItem("Turn off %s" % name, toggle, (item, var))
    return menu.MenuItem("Turn on %s" % name, toggle, (item, var))

    
#
# config main menu
#

def main_menu_generate(item):
    next_start = 0
    items = []

    if item.available_audio_tracks:
        items += [ menu.MenuItem("Audio selection", audio_selection_menu, item) ]
        
    if item.available_subtitles:
        items += [ menu.MenuItem("Subtitle selection", subtitle_selection_menu, item) ]
        
    if item.available_chapters > 1:
        items += [ menu.MenuItem("Chapter selection", chapter_selection_menu, item) ]
        
    items += [ add_toogle('deinterlacing', item, 'deinterlace') ]
    items += [ menu.MenuItem("Play", play_movie, (item, '')) ]

    return items

        
def get_main_menu(item, menuw, xml_file):
    global current_xml_file
    current_xml_file = xml_file
    return menu.Menu('CONFIG MENU', main_menu_generate(item), xml_file=xml_file)
    

###########################



RE_AUDIO = re.compile("^\[open\] audio stream: [0-9] audio format:(.*)aid: ([0-9]*)").match
RE_SUBTITLE = re.compile("^\[open\] subtitle.*: ([0-9]) language: ([a-z][a-z])").match
RE_CHAPTER = re.compile("^There are ([0-9]*) chapters in this DVD title.").match


#
# parser
#

def parse(str, item):
    m = self.RE_AUDIO(str)
    if m: item.available_audio_tracks += [ (m.group(2), m.group(1)) ]

    m = self.RE_SUBTITLE(str)
    if m: item.available_subtitles += [ (m.group(1), m.group(2)) ]

    m = self.RE_CHAPTER(str)
    if m: item.available_chapters = int(m.group(1))
    
