# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# imdb.py - Plugin for IMDB support
# -----------------------------------------------------------------------
# $Id$
#
# Notes: IMDB plugin. You can add IMDB informations for video items
#        with the plugin
#        activate with plugin.activate('video.imdb')
#        You can also set imdb_search on a key (e.g. '1') by setting
#        EVENTS['menu']['1'] = Event(MENU_CALL_ITEM_ACTION, arg='imdb_search_or_cover_search')
#
# Todo:  - function to add to an existing fxd file
#        - DVD/VCD support
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.37  2004/07/22 21:21:50  dischi
# small fixes to fit the new gui code
#
# Revision 1.36  2004/07/10 12:33:43  dischi
# header cleanup
#
# Revision 1.35  2004/06/02 21:36:50  dischi
# auto detect movies with more than one file
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


import os

import menu
import config
import plugin
import re
import time
from util.fxdimdb import FxdImdb, makeVideo, makePart, point_maker

from gui import PopupBox
from util import htmlenties2txt

class PluginInterface(plugin.ItemPlugin):
    def __init__(self, license=None):
        if not config.USE_NETWORK:
            self.reason = 'no network'
            return
        plugin.ItemPlugin.__init__(self)

    
    def imdb_get_disc_searchstring(self, item):
        name  = item.media.label
        name  = re.sub('([a-z])([A-Z])', point_maker, name)
        name  = re.sub('([a-zA-Z])([0-9])', point_maker, name)
        name  = re.sub('([0-9])([a-zA-Z])', point_maker, name.lower())
        for r in config.IMDB_REMOVE_FROM_LABEL:
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

        if item.type == 'video' and (not item.files or not item.files.fxd_file):
            if item.mode == 'file' or (item.mode in ('dvd', 'vcd') and \
                                       item.info.has_key('tracks') and not \
                                       item.media):
                self.disc_set = False
                return [ ( self.imdb_search , _('Search IMDB for this file'),
                           'imdb_search_or_cover_search') ]
            
            elif item.mode in ('dvd', 'vcd') and item.info.has_key('tracks'):
                self.disc_set = True
                s = self.imdb_get_disc_searchstring(self.item)
                if s:
                    return [ ( self.imdb_search , _('Search IMDB for [%s]') % s,
                               'imdb_search_or_cover_search') ]

        if item.type == 'dir' and item.media and item.media.mountdir.find(item.dir) == 0:
            self.disc_set = True
            s = self.imdb_get_disc_searchstring(self.item)
            if s:
                return [ ( self.imdb_search , _('Search IMDB for [%s]') % s,
                           'imdb_search_or_cover_search') ]
        return []

            
    def imdb_search(self, arg=None, menuw=None):
        """
        search imdb for this item
        """
        fxd = FxdImdb()

        box = PopupBox(text=_('searching IMDB...'))
        box.show()

        items = []
        
        try:
            duplicates = []
            if self.disc_set:
                self.searchstring = self.item.media.label
            else:
                self.searchstring = self.item.name
                
            for id,name,year,type in fxd.guessImdb(self.searchstring, self.disc_set):
                try:
                    for i in self.item.parent.play_items:
                        if i.name == name:
                            if not i in duplicates:
                                duplicates.append(i)
                except:
                    pass
                items.append(menu.MenuItem('%s (%s, %s)' % (htmlenties2txt(name), year, type),
                                           self.imdb_create_fxd, (id, year)))
        except:
            box.destroy()
            box = PopupBox(text=_('Unknown error while connecting to IMDB'))
            box.show()
            time.sleep(2)
            box.destroy()
            return
        
        # for d in duplicates:
        #     items = [ menu.MenuItem('Add to "%s"' % d.name,
        #                             self.imdb_add_to_fxd, (d, 'add')),
        #               menu.MenuItem('Variant to "%s"' % d.name,
        #                             self.imdb_add_to_fxd, (d, 'variant')) ] + items

        box.destroy()
        if config.IMDB_AUTOACCEPT_SINGLE_HIT and len(items) == 1:
            self.imdb_create_fxd(arg=items[0].arg, menuw=menuw)
            return

        if items: 
            moviemenu = menu.Menu(_('IMDB Query'), items)
            menuw.pushmenu(moviemenu)
            return

        box = PopupBox(text=_('No information available from IMDB'))
        box.show()
        time.sleep(2)
        box.destroy()
        return


    def imdb_menu_back(self, menuw):
        """
        check how many menus we have to go back to see the item
        """
        import directory

        # check if we have to go one menu back (called directly) or
        # two (called from the item menu)
        back = 1
        if menuw.menustack[-2].selected != self.item:
            back = 2
            
        # maybe we called the function directly because there was only one
        # entry and we called it with an event
        if menuw.menustack[-1].selected == self.item:
            back = 0
            
        # update the directory
        if directory.dirwatcher:
            directory.dirwatcher.scan()

        # go back in menustack
        for i in range(back):
            menuw.delete_menu()
        
        
    def imdb_create_fxd(self, arg=None, menuw=None):
        """
        create fxd file for the item
        """
        fxd = FxdImdb()
        
        box = PopupBox(text=_('getting data...'))
        box.show()

        #if this exists we got a cdrom/dvdrom
        if self.item.media and self.item.media.devicename: 
            devicename = self.item.media.devicename
        else:
            devicename = None
        
        fxd.setImdbId(arg[0])
        
        if self.disc_set:
            fxd.setDiscset(devicename, None)
        else:
            if self.item.subitems:
                for i in range(len(self.item.subitems)):
                    video = makeVideo('file', 'f%s' % i,
                                      os.path.basename(self.item.subitems[i].filename),
                                      device=devicename)
                    fxd.setVideo(video)
            else:
                video = makeVideo('file', 'f1', os.path.basename(self.item.filename),
                                  device=devicename)
                fxd.setVideo(video)
            fxd.setFxdFile(os.path.splitext(self.item.filename)[0])

        fxd.writeFxd()
        self.imdb_menu_back(menuw)
        box.destroy()


    def imdb_add_to_fxd(self, arg=None, menuw=None):
        """
        add item to fxd file
        BROKEN, PLEASE FIX
        """

        #if this exists we got a cdrom/dvdrom
        if self.item.media and self.item.media.devicename: 
            devicename = self.item.media.devicename
        else: devicename = None
        
        fxd = FxdImdb()
        fxd.setFxdFile(arg[0].fxd_file)

        if self.item.mode in ('dvd', 'vcd'):
            fxd.setDiscset(devicename, None)
        else:
            num = len(fxd.video) + 1
            video = makeVideo('file', 'f%s' % num, self.item.filename, device=devicename)
            fxd.setVideo(video)

            if arg[1] == 'variant':
                part = makePart('Variant %d' % num, 'f%s' % num)

                if fxd.variant:
                    part = [ makePart('Variant 1', 'f1'), part ]

                fxd.setVariants(part)
            
        fxd.writeFxd()
        self.imdb_menu_back(menuw)
