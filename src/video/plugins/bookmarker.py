# -*- coding: iso-8859-1 -*-
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
# Revision 1.14  2004/08/24 16:42:44  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.13  2004/07/26 18:10:20  dischi
# move global event handling to eventhandler.py
#
# Revision 1.12  2004/07/10 12:33:43  dischi
# header cleanup
#
# Revision 1.11  2004/02/22 20:33:48  dischi
# some unicode fixes
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


import os, time, copy
import mmpython

import plugin
import config
import util
import menu
import eventhandler

from event import *

class PluginInterface(plugin.ItemPlugin):
    """
    class to handle auto bookmarks
    """
    def actions(self, item):
        self.item = item
        items = []
        if item['autobookmark_resume']:
            items.append((self.resume, _('Resume playback')))
        if item.type == 'dir' or item.type == 'playlist':
            return items    
        if item.mode == 'file' and not item.variants and \
               not item.subitems and os.path.exists(util.get_bookmarkfile(item.filename)):
            items.append(( self.bookmark_menu, _('Bookmarks')))
            
        return items


    def resume(self, arg=None, menuw=None):
        """
        resume playback
        """
        t    = max(0, self.item['autobookmark_resume'] - 10)
        info = mmpython.parse(self.item.filename)
        if hasattr(info, 'seek') and t:
            arg='-sb %s' % info.seek(t)
        else:
            arg='-ss %s' % t
        if menuw:
            menuw.back_one_menu()
        self.item.play(menuw=menuw, arg=arg)

        
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
            file.name = Unicode(_('Jump to %s') % (time))
            if hasattr(file, 'tv_show'):
                del file.tv_show
            
            if not self.item.mplayer_options:
                self.item.mplayer_options = ''
            file.mplayer_options = str(self.item.mplayer_options) +  ' -ss %s' % time
            items.append(file)

        if items:
            moviemenu = menu.Menu(self.item.name, items, theme=self.item.skin_fxd)
            menuw.pushmenu(moviemenu)
        return

        
    def eventhandler(self, item, event, menuw):
        if event in (STOP, USER_END):
            if item.mode == 'file' and not item.variants and \
                   not item.subitems and item.elapsed:
                item.store_info('autobookmark_resume', item.elapsed)
            else:
                _debug_('auto-bookmark not supported for this item')
                
        if event == PLAY_END:
            item.delete_info('autobookmark_resume')


        # Bookmark the current time into a file
        if event == STORE_BOOKMARK:
            bookmarkfile = util.get_bookmarkfile(item.filename)
            
            handle = open(bookmarkfile,'a+') 
            handle.write(str(item.elapsed))
            handle.write('\n')
            handle.close()
            eventhandler.post(Event(OSD_MESSAGE, arg='Added Bookmark'))
            return True

        return False
    
