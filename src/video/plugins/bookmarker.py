#if 0 /*
# -----------------------------------------------------------------------
# bookmarker.py - Plugin to handle bookmarking
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#     1. while watching a movie file, hit the 'record' button and it'll save a
#        bookmark. There is no visual feedback though.
#     2. Later, to get back there, choose the actions button in the menu, and it'll
#        have a list of bookmarks in a submenu, click on one of those to resume from
#        where you saved.
#     3. When stopping a movie while blackback, the current playtime will be stored
#        in an auto bookmark file. After that, a RESUME action is in the item
#        menu to start were the plackback stopped.
#
# Todo:
#     Currently this only works for files without subitems or variant. 
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/08/30 17:09:10  dischi
# o video bookmarks are now handled inside this plugin
# o support for auto bookmark: save positon when you STOP the playback
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

import os, time, copy

import plugin
import config
import util
import menu

from event import *

FALSE = 0
TRUE = 1

class PluginInterface(plugin.ItemPlugin):
    """
    class to handle auto bookmarks
    """
    def __init__(self):
        plugin.ItemPlugin.__init__(self)
        self.VERSION = 1
        self.file = os.path.join(config.FREEVO_CACHEDIR, 'autobookmarks-%s' % os.getuid())
        try:
            version, self.bookmarks = util.read_pickle(self.file)
            if version != self.VERSION:
                self.bookmarks = {}
        except:
            self.bookmarks = {}


    def __get_auto_bookmark__(self, item):
        try:
            return self.bookmarks[item.getattr('item_id')][1]
        except KeyError:
            return 0
        

    def actions(self, item):
        self.item = item
        items = []
        ab = self.__get_auto_bookmark__(item)
        if ab:
            items.append((self.resume, 'Resume playback'))
            
        if item.mode == 'file' and not item.variants and \
               not item.subitems and os.path.exists(util.get_bookmarkfile(item.filename)):
            items.append(( self.bookmark_menu, 'Bookmarks'))
            
        return items


    def resume(self, arg=None, menuw=None):
        """
        resume playback
        """
        ab = self.__get_auto_bookmark__(self.item)
        if ab:
            t = max(0, ab - 10)
        else:
            t = 0
        if menuw:
            menuw.back_one_menu()
        self.item.play(menuw=menuw, arg='-ss %s' % t)

        
    def bookmark_menu(self,arg=None, menuw=None):
        """
        Bookmark list
        """
        bookmarkfile = util.get_bookmarkfile(self.item.filename)
        items = []
        for line in util.readfile(bookmarkfile):
            file = copy.copy(self.item)
            file.info = {}
            
            sec = int(line)
            hour = int(sec/3600)
            min = int((sec-(hour*3600))/60)
            sec = int(sec%60)
            time = '%0.2d:%0.2d:%0.2d' % (hour,min,sec)
            # set a new title
            file.name = 'Jump to %s' % (time)
            if hasattr(file, 'tv_show'):
                del file.tv_show
            
            if not self.item.mplayer_options:
                self.item.mplayer_options = ''
            file.mplayer_options = str(self.item.mplayer_options) +  ' -ss %s' % time
            items.append(file)

        if items:
            moviemenu = menu.Menu(self.item.name, items, xml_file=self.item.xml_file)
            menuw.pushmenu(moviemenu)
        return

        
    def eventhandler(self, item, event, menuw):
        if event in (STOP, USER_END):
            if item.mode == 'file' and not item.variants and \
                   not item.subitems and item.elapsed:
                self.bookmarks[item.getattr('item_id')] = (time.time, item.elapsed)
                util.save_pickle((self.VERSION, self.bookmarks), self.file)
            elif config.DEBUG:
                print 'auto-bookmark not supported for this item'
                
        if event == PLAY_END:
            try:
                del self.bookmarks[item.getattr('item_id')]
                util.save_pickle((self.VERSION, self.bookmarks), self.file)
            except:
                pass

        # Bookmark the current time into a file
        if event == STORE_BOOKMARK:
            bookmarkfile = util.get_bookmarkfile(item.filename)
            
            handle = open(bookmarkfile,'a+') 
            handle.write(str(item.elapsed))
            handle.write('\n')
            handle.close()
            return TRUE

        return FALSE
    
