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
# Revision 1.13  2003/08/02 10:09:52  dischi
# Don't add 'Settings' with a submenu to the list of actions, add the
# settings directly (max 4 items, mostly 1)
#
# Revision 1.12  2003/07/25 20:54:29  dischi
# make audio selection work for files, too
#
# Revision 1.11  2003/06/29 20:43:30  dischi
# o mmpython support
# o mplayer is now a plugin
#
# Revision 1.10  2003/04/24 19:56:42  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.9  2003/04/12 18:30:04  dischi
# add support for audio/subtitle selection for avis, too
#
# Revision 1.8  2003/03/31 20:44:52  dischi
# shorten time between pop.destroy and menu drawing
#
# Revision 1.7  2003/03/30 16:50:20  dischi
# pass xml_file definition to submenus
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
import plugin

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
    for a in arg.info['audio']:
        if not a['id']:
            a['id'] = arg.info['audio'].index(a) + 1
        if not a['language']:
            a['language'] = 'Unknown'
        txt = '%s (channels=%s, codec=%s, id=%s)' % (a['language'], a['channels'],
                                                     a['codec'], a['id'])
        items.append(menu.MenuItem(txt, audio_selection, (arg, a['id'])))
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
    for s in range(len(arg.info['subtitles'])):
        items.append(menu.MenuItem(arg.info['subtitles'][s], subtitle_selection, (arg, s)))
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
    for c in range(1, arg.info['chapters']):
        items += [ menu.MenuItem("play chapter %s" % c, chapter_selection,
                                 (arg, ' -chapter %s' % c)) ]
    moviemenu = menu.Menu('CHAPTER MENU', items, xml_file=current_xml_file)
    menuw.pushmenu(moviemenu)


#
# De-interlacer
#

def toggle(arg=None, menuw=None):
    setattr(arg[1], arg[2], not getattr(arg[1], arg[2]))

    old = menuw.menustack[-1].selected
    pos = menuw.menustack[-1].choices.index(menuw.menustack[-1].selected)

    new = add_toogle(arg[0], arg[1], arg[2])
    new.image = old.image
    new.display_type = old.display_type
    
    menuw.menustack[-1].choices[pos] = new
    menuw.menustack[-1].selected = menuw.menustack[-1].choices[pos]

    menuw.init_page()
    menuw.refresh()


def add_toogle(name, item, var):
    if getattr(item, var):
        return menu.MenuItem("Turn off %s" % name, toggle, (name, item, var))
    return menu.MenuItem("Turn on %s" % name, toggle, (name, item, var))

    
#
# config main menu
#

def get_items(item):
    next_start = 0
    items = []

    if not ((not item.filename or item.filename == '0') and \
            item.mode == 'dvd' and plugin.getbyname(plugin.DVD_PLAYER)):

        if item.info.has_key('audio') and len(item.info['audio']) > 1:
            items.append(menu.MenuItem("Audio selection", audio_selection_menu, item))
        if item.info.has_key('subtitles') and len(item.info['subtitles']) > 1:
            items.append(menu.MenuItem("Subtitle selection", subtitle_selection_menu, item))
        if item.info.has_key('chapters') and item.info['chapters'] > 1:
            items.append(menu.MenuItem("Chapter selection", chapter_selection_menu, item))

    items += [ add_toogle('deinterlacing', item, 'deinterlace') ]
    return items

        
def get_menu(item, menuw, xml_file):
    global current_xml_file
    current_xml_file = xml_file

    items = get_items(item) + [ menu.MenuItem("Play", play_movie, (item, '')) ]
    return menu.Menu('CONFIG MENU', items, xml_file=xml_file)
    
