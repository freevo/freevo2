#if 0 /*
# -----------------------------------------------------------------------
# imdb.py - Plugin for IMDB support
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This is an example how plugins work
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/01/07 20:43:39  dischi
# Small fixes, the actions get the item as arg
#
# Revision 1.3  2003/01/07 19:44:29  dischi
# small bugfix
#
# Revision 1.2  2002/12/30 15:57:06  dischi
# Added search for DVD/VCD to the item menu. You can only search the disc
# label and you can't insert your own search text
#
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

def actions(item):
    if (not item.type == 'video') or item.mode == 'file' or item.rom_id or item.rom_label:
        return []
    return [ (imdb_search_disc, 'Search IMDB for [%s]' % item.label),
             (imdb_add_disc_menu, 'Add disc to existing entry in database') ]

# -------------------------------------------

def imdb_search_disc(arg=None, menuw=None):
    """
    search imdb for this disc
    """
    import helpers.imdb

    skin.PopupBox('searching IMDB, be patient...')
    osd.update()

    items = []
    for id,name,year,type in helpers.imdb.search(arg.label):
        items += [ menu.MenuItem('%s (%s, %s)' % (name, year, type),
                                 imdb_create_disc, (id, year)) ]
    moviemenu = menu.Menu('IMDB QUERY', items)
    menuw.pushmenu(moviemenu)


def imdb_create_disc(arg=None, menuw=None):
    """
    get imdb informations and store them
    """
    import helpers.imdb

    skin.PopupBox('getting data, be patient...')
    osd.update()
    menuw.delete_menu()
    menuw.delete_menu()

    disc_id = helpers.imdb.getCDID(arg.media.devicename)
    filename = ('%s/%s_%s' % (config.MOVIE_DATA_DIR, arg.label, \
                              arg[1])).lower()
    if os.path.isfile('%s.xml' % filename):
        filename = '%s_%s' % (filename, disc_id)

    helpers.imdb.get_data_and_write_xml(arg[0], filename, disc_id,
                                        arg.mode,None)
    
# -------------------------------------------

def imdb_add_disc(arg=None, menuw=None):
    """
    call imdb.py to add this disc to the database
    """
    import helpers.imdb

    skin.PopupBox('adding to database, be patient...')
    osd.update()
    menuw.delete_menu()
    menuw.delete_menu()

    helpers.imdb.add_id(arg.media.devicename, arg.xml_file)


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
