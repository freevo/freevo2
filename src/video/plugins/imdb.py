#if 0 /*
# -----------------------------------------------------------------------
# imdb.py - Plugin for IMDB support
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This is an example who plugins work
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/12/07 13:33:08  dischi
# plugin example: add discs to imdb.py xml files
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

import os

import config
import menu
import skin
import osd

skin = skin.get_singleton()
osd  = osd.get_singleton()

current_media = None

def actions(item):
    global current_media
    if (not item.type == 'video') or item.mode == file or item.rom_id or item.rom_label:
        return []
    current_media = item.media
    return [ (imdb_add_disc_menu, 'Add disc to existing entry in database') ]

# -------------------------------------------

def imdb_add_disc(arg=None, menuw=None):
    """
    call imdb.py to add this disc to the database
    """
    global current_media
    skin.PopupBox('adding to database, be patient...')
    osd.update()
    menuw.delete_menu()
    menuw.delete_menu()

    os.system('./helpers/imdb.py --add-id %s %s' % \
              (current_media.devicename, arg.xml_file))


def imdb_add_disc_menu(arg=None, menuw=None):
    """
    make a list of all movies in config.MOVIE_DATA_DIR to select
    one item
    """
    items = []
    for m in config.MOVIE_INFORMATIONS:
        # add all items with a name and when the name is not made to be
        # a label regexp
        if m.name and m.name.find('\\') == -1:
            i = menu.MenuItem(m.name, imdb_add_disc, m)
            if m.image:
                i.handle_type  = m.type
                i.image = m.image
            items += [ i ]

    items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))
    moviemenu = menu.Menu('DVD/VCD DATABASE', items)
    menuw.pushmenu(moviemenu)
