#if 0 /*
# -----------------------------------------------------------------------
# imdb.py - Plugin for IMDB support
# -----------------------------------------------------------------------
# $Id$
#
# Notes: IMDB plugin. You can add IMDB informations for video items
#        with the plugin
#        activate with plugin.activate('video.imdb')
#        You can also set imdb_search on a key (e.g. '1') by setting
#        EVENTS['menu']['1'] = Event(MENU_CALL_ITEM_ACTION, arg='imdb_search')
#
# Todo:  - function to add to an existing fxd file
#        - DVD/VCD support
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2003/06/23 19:52:55  dischi
# change event key to imdb_search_or_cover_search
#
# Revision 1.8  2003/06/09 14:45:16  dischi
# add support for DVD/VCD
#
# Revision 1.7  2003/06/07 11:32:48  dischi
# reactivated the plugin
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

import menu
import config
import plugin
import re

from gui.PopupBox import PopupBox


def point_maker(matching):
    """
    small help function to split a movie name into parts
    """
    return '%s.%s' % (matching.groups()[0], matching.groups()[1])


remove_from_label = ('season[\._ -][0-9]+', 'disc[\._ -][0-9]+')

class PluginInterface(plugin.ItemPlugin):
    def imdb_get_disc_searchstring(self, item):
        name = self.item.filename
        
        name  = item.label
        name  = re.sub('([a-z])([A-Z])', point_maker, name)
        name  = re.sub('([a-zA-Z])([0-9])', point_maker, name)
        name  = re.sub('([0-9])([a-zA-Z])', point_maker, name.lower())

        for r in remove_from_label:
            name  = re.sub(r, '', name)

        parts = re.split('[\._ -]', name)
        
        name = ''
        for p in parts:
            if p:
                name += '%s ' % p
        if name:
            return name[:-1]
        else:
            return ''

        
    def actions(self, item):
        self.item = item

        if item.type == 'video'  and not item.info:
            if item.mode == 'file':
                return [ ( self.imdb_search_file, 'Search IMDB for this file',
                           'imdb_search_or_cover_search') ]
            if item.mode in ('dvd', 'vcd'):
                s = self.imdb_get_disc_searchstring(self.item)
                if s:
                    return [ ( self.imdb_search_disc, 'Search IMDB for [%s]' % s,
                               'imdb_search_or_cover_search') ]
        return []


    def imdb_search_disc(self, arg=None, menuw=None):
        """
        search imdb for this disc item
        """
        import helpers.imdb

        box = PopupBox(text='searching IMDB...')
        box.show()
        
        name = self.imdb_get_disc_searchstring(self.item)
        items = []
        for id,name,year,type in helpers.imdb.search(name):
            items += [ menu.MenuItem('%s (%s, %s)' % (name, year, type),
                                     self.imdb_create_fxd_disc, (id, year)) ]
        moviemenu = menu.Menu('IMDB QUERY', items)

        box.destroy()
        menuw.pushmenu(moviemenu)


    def imdb_create_fxd_disc(self, arg=None, menuw=None):
        """
        create fxd file for the disc item
        """
        import helpers.imdb
        
        box = PopupBox(text='getting data...')
        box.show()
        
        filename = os.path.join(config.MOVIE_DATA_DIR, self.item.media.id)

        # bad hack to set the drive, helpers/imdb.py really needs
        # a bigger update
        helpers.imdb.drive = self.item.media.devicename
        helpers.imdb.get_data_and_write_fxd(arg[0], filename,
                                            self.item.media.devicename,
                                            None, (self.item.mode, ), None)

        # check if we have to go one menu back (called directly) or
        # two (called from the item menu)
        back = 1
        if menuw.menustack[-2].selected != self.item:
            back = 2
            
        # go back in menustack
        for i in range(back):
            menuw.delete_menu()
        
        box.destroy()

            
    def imdb_search_file(self, arg=None, menuw=None):
        """
        search imdb for this item
        """
        import helpers.imdb

        box = PopupBox(text='searching IMDB...')
        box.show()
        
        name = self.item.filename
        
        name  = os.path.basename(os.path.splitext(name)[0])
        name  = re.sub('([a-z])([A-Z])', point_maker, name)
        name  = re.sub('([a-zA-Z])([0-9])', point_maker, name)
        name  = re.sub('([0-9])([a-zA-Z])', point_maker, name.lower())
        parts = re.split('[\._ -]', name)
        
        name = ''
        for p in parts:
            name += '%s ' % p
        
        items = []
        for id,name,year,type in helpers.imdb.search(name):
            items += [ menu.MenuItem('%s (%s, %s)' % (name, year, type),
                                     self.imdb_create_fxd, (id, year)) ]
        moviemenu = menu.Menu('IMDB QUERY', items)

        box.destroy()
        menuw.pushmenu(moviemenu)


    def imdb_create_fxd(self, arg=None, menuw=None):
        """
        create fxd file for the item
        """
        import helpers.imdb
        import directory
        
        box = PopupBox(text='getting data...')
        box.show()
        
        filename = os.path.splitext(self.item.filename)[0]
        helpers.imdb.get_data_and_write_fxd(arg[0], filename, None, None,
                                            (self.item.filename, ), None)

        # check if we have to go one menu back (called directly) or
        # two (called from the item menu)
        back = 1
        if menuw.menustack[-2].selected != self.item:
            back = 2
            
        # update the directory
        if directory.dirwatcher_thread:
            directory.dirwatcher_thread.scan()

        # go back in menustack
        for i in range(back):
            menuw.delete_menu()
        
        box.destroy()
