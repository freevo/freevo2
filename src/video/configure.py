# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# configure.py - Configure video playing
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

# python imports
import re

# freevo imports
import menu
import plugin


#
# Dummy for playing the movie
#

def play_movie(arg=None, menuw=None):
    """
    play the movie (again)
    """
    menuw.delete_menu()
    arg[0].play(menuw=menuw, arg=arg[1])



#
# Audio menu and selection
#

def audio_selection(arg=None, menuw=None):
    """
    Handle audio selection.
    """
    arg[0].selected_audio = arg[1]
    menuw.back_one_menu()


def audio_selection_menu(arg=None, menuw=None):
    """
    Submenu for audio selection.
    """
    item = arg
    menu_items = []

    for a in item.info['audio']:
        if not a.has_key('id') or a['id'] in ('', None):
            a['id'] = item.info['audio'].index(a) + 1

        if not a.has_key('language') or not a['language']:
            a['language'] = _('Stream %s') % a['id']

        if not a.has_key('channels') or not a['channels']:
            a['channels'] = 2 # wild guess :-)

        txt = '%s (channels=%s)' % (a['language'], a['channels'])
        menu_items.append(menu.MenuItem(txt, audio_selection, (item, a['id'])))

    moviemenu = menu.Menu(_('Audio Menu'), menu_items, theme=item.skin_fxd)
    menuw.pushmenu(moviemenu)


#
# Subtitle menu and selection
#

def subtitle_selection(arg=None, menuw=None):
    """
    Handle subtitle selection.
    """
    arg[0].selected_subtitle = arg[1]
    menuw.back_one_menu()

def subtitle_selection_menu(arg=None, menuw=None):
    """
    Submenu for subtitle selection.
    """
    item = arg
    menu_items = [ menu.MenuItem(_('no subtitles'), subtitle_selection,
                                 (item, -1)) ]
    for s in range(len(item.info['subtitles'])):
        menu_items.append(menu.MenuItem(item.info['subtitles'][s],
                                        subtitle_selection, (item, s)))
    moviemenu = menu.Menu(_('Subtitle Menu'), menu_items, theme=item.skin_fxd)
    menuw.pushmenu(moviemenu)


#
# Chapter selection
#

def chapter_selection(menuw=None, arg=None):
    """
    Handle chapter selection.
    """
    menuw.delete_menu()
    play_movie(menuw=menuw, arg=arg)

def chapter_selection_menu(arg=None, menuw=None):
    """
    Submenu for chapter selection.
    """
    item  = arg
    menu_items = []
    if isinstance(arg.info['chapters'], int):
        for c in range(1, arg.info['chapters']):
            menu_items += [ menu.MenuItem(_('Play chapter %s') % c,
                                          chapter_selection,
                                          (arg, ' -chapter %s' % c)) ]
    elif arg.info['chapters']:
        for c in arg.info['chapters']:
            menu_items += [ menu.MenuItem(c.name, chapter_selection,
                                          (arg, ' -ss %s' % c.pos)) ]

    moviemenu = menu.Menu(_('Chapter Menu'), menu_items, theme=item.skin_fxd)
    menuw.pushmenu(moviemenu)


#
# Chapter selection
#

def subitem_selection(menuw=None, arg=None):
    """
    Handle subitem selection.
    """
    item, pos = arg
    item.conf_select_this_item = item.subitems[pos]
    menuw.delete_menu()
    play_movie(menuw=menuw, arg=(item, None))


def subitem_selection_menu(arg=None, menuw=None):
    """
    Submenu for subitem selection.
    """
    item  = arg
    menu_items = []
    for pos in range(len(item.subitems)):
        menu_items += [ menu.MenuItem(_('Play chapter %s') % (pos+1),
                                      subitem_selection, (arg, pos)) ]
    moviemenu = menu.Menu(_('Chapter Menu'), menu_items,
                          fxd_file=item.skin_fxd)
    menuw.pushmenu(moviemenu)


#
# De-interlacer
#

def toggle(arg=None, menuw=None):
    """
    Basic toggle function.
    """
    arg[1][arg[2]] = not arg[1][arg[2]]

    old = menuw.menustack[-1].selected
    pos = menuw.menustack[-1].choices.index(menuw.menustack[-1].selected)

    new = add_toogle(arg[0], arg[1], arg[2])
    new.image = old.image

    if hasattr(old, 'display_type'):
        new.display_type = old.display_type

    menuw.menustack[-1].choices[pos] = new
    menuw.menustack[-1].selected = menuw.menustack[-1].choices[pos]

    menuw.refresh()


def add_toogle(name, item, var):
    """
    Add a 'toggle' item.
    """
    if item[var]:
        return menu.MenuItem(_('Turn off %s') % name, toggle,
                             (name, item, var))
    return menu.MenuItem(_('Turn on %s') % name, toggle, (name, item, var))




#
# config main menu
#

def get_items(item):
    """
    Return possible configure items.
    """
    next_start = 0
    items = []

    print item.subitems
    if item.filename or (item.mode in ('dvd', 'vcd') and \
                         item.player_rating >= 20):
        if item.info.has_key('audio') and len(item.info['audio']) > 1:
            items.append(menu.MenuItem(_('Audio selection'),
                                       audio_selection_menu, item))
        if item.info.has_key('subtitles') and len(item.info['subtitles']) > 1:
            items.append(menu.MenuItem(_('Subtitle selection'),
                                       subtitle_selection_menu, item))
        if item.info.has_key('chapters') and item.info['chapters'] > 1:
            items.append(menu.MenuItem(_('Chapter selection'),
                                       chapter_selection_menu, item))
    if item.subitems:
        # show subitems as chapter
        items.append(menu.MenuItem(_('Chapter selection'),
                                   subitem_selection_menu, item))

    if item.mode in ('dvd', 'vcd') or \
           (item.filename and item.info.has_key('type') and \
            item.info['type'] and \
            item.info['type'].lower().find('mpeg') != -1):
        items += [ add_toogle(_('deinterlacing'), item, 'deinterlace') ]
    return items


def get_menu(item, menuw):
    """
    Return a complete menu for configure options.
    """
    items = get_items(item) + [ menu.MenuItem(_('Play'), play_movie,
                                              (item, '')) ]
    return menu.Menu(_('Config Menu'), items, theme=item.skin_fxd)

