#if 0 /*
# -----------------------------------------------------------------------
# coverserarch.py - Plugin for album cover support
# -----------------------------------------------------------------------
# $Id$
#
# Notes: This plugin will allow you to find album covers. At first, only
#        Amazon is supported. Someone could easily add allmusic.com support
#        which is more complete, but lacks a general interface like amazon's
#        web services.
#
#        You also need an Amazon developer key.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/06/07 18:43:26  outlyer
# The beginnings of a cover search plugin to complement Dischi's IMDB plugin
# for video. Currently, it uses the ID3 tag to find the album cover from
# amazon and prints the url on the screen.
#
# It doesn't do anything with it yet, because I still need to add a submenu
# to allow the user to choose:
#
# 1. Write a per-song cover (i.e. song_filename.jpg)
# 2. Write a per-album/directory cover (i.e. cover.jpg)
#
# If you want to see it in action, you can do a:
#
# plugin.activate('audio.coversearch')
#
# This only uses Amazon now, but could easily be extended to use allmusic.com
# if someone writes something to interface with it. Amazon was dead-simple
# to use, so I did it first, though Amazon is pretty weak, selection-wise
# compared to allmusic.com
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
import plugin
import re

from gui.PopupBox import PopupBox


class PluginInterface(plugin.ItemPlugin):
    def actions(self, item):
        self.item = item

        if item.type == 'audio':
            return [ ( self.cover_search_file, 'Find a cover for this music', 'cover_search') ]
        return []


    def cover_search_file(self, arg=None, menuw=None):
        """
        search imdb for this item
        """
        import amazon

        box = PopupBox(text='searching Amazon...')
        box.show()
        
        album = self.item.album
        artist = self.item.artist

        amazon.setLicense('...') # must get your own key!
        cover = amazon.searchByKeyword('%s %s' % (artist,album) , product_line="music")
        print cover[0].ImageUrlLarge

        #name  = os.path.basename(os.path.splitext(name)[0])
        #name  = re.sub('([a-z])([A-Z])', point_maker, name)
        #name  = re.sub('([a-zA-Z])([0-9])', point_maker, name)
        #name  = re.sub('([0-9])([a-zA-Z])', point_maker, name.lower())
        #parts = re.split('[\._ -]', name)
        
        #name = ''
        #for p in parts:
        #    name += '%s ' % p
        
        #items = []
        #for id,name,year,type in helpers.imdb.search(name):
        #    items += [ menu.MenuItem('%s (%s, %s)' % (name, year, type),
                                     #self.imdb_create_fxd, (id, year)) ]
        #moviemenu = menu.Menu('IMDB QUERY', items)

        box.destroy()
        #menuw.pushmenu(moviemenu)
        print album
        print artist
        box = PopupBox(text='Artist: %s\nAlbum: %s\nURL: %s\n' % (str(artist), str(album),str(cover[0].ImageUrlLarge)))
        box.show()
        import time
        time.sleep(2)
        box.destroy()
        return


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
