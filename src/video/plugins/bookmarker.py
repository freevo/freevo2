# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# bookmarker.py - Plugin to handle bookmarking
# -----------------------------------------------------------------------------
# $Id$
#
# 1. while watching a movie file, hit the 'record' button and it'll save a
#    bookmark. There is no visual feedback though.
# 2. Later, to get back there, choose the actions button in the menu, and it'll
#    have a list of bookmarks in a submenu, click on one of those to resume
#    from where you saved.
# 3. When stopping a movie while blackback, the current playtime will be stored
#    in as auto bookmark. After that, a RESUME action is in the item menu to
#    start were the plackback stopped.
#
# Todo: Currently this only works for files without subitems or variant.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Aubin Paul <aubin@outlyer.org>
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
import os
import copy
import logging
import mmpython

# freevo imports
import sysconfig
import plugin
import util
import menu
import eventhandler

from event import *

# get logging object
log = logging.getLogger('video')

class PluginInterface(plugin.ItemPlugin):
    """
    class to handle auto bookmarks
    """
    def get_bookmarkfile(filename):
        """
        Get the bookmark file for the given filename.
        """
        myfile = os.path.basename(filename)
        myfile = sysconfig.CACHEDIR + "/" + myfile + '.bookmark'
        return myfile


    def actions(self, item):
        """
        Return additional actions for the item.
        """
        if item.type == 'dir' or item.type == 'playlist':
            # only works for video items
            return []
        # store item
        self.item = item
        # create actions
        items = []
        if item['autobookmark_resume']:
            items.append((self.resume, _('Resume playback')))
        if item.mode == 'file' and not item.variants and not item.subitems \
               and os.path.exists(self.get_bookmarkfile(item.filename)):
            items.append(( self.bookmark_menu, _('Bookmarks')))
        return items


    def resume(self, arg=None, menuw=None):
        """
        Resume playback
        """
        t = max(0, self.item['autobookmark_resume'] - 10)
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
        bookmarkfile = self.get_bookmarkfile(self.item.filename)
        items = []
        for line in util.readfile(bookmarkfile):
            file = copy.copy(self.item)
            file.info = {}

            sec  = int(line)
            hour = int(sec/3600)
            min  = int((sec-(hour*3600))/60)
            sec  = int(sec%60)
            time = '%0.2d:%0.2d:%0.2d' % (hour,min,sec)
            # set a new title
            file.name = Unicode(_('Jump to %s') % (time))
            if hasattr(file, 'tv_show'):
                del file.tv_show

            if not self.item.mplayer_options:
                self.item.mplayer_options = ''
            file.mplayer_options = str(self.item.mplayer_options) +  \
                                   ' -ss %s' % time
            items.append(file)

        if items:
            moviemenu = menu.Menu(self.item.name, items,
                                  theme=self.item.skin_fxd)
            menuw.pushmenu(moviemenu)
        return


    def eventhandler(self, item, event, menuw):
        """
        Handle video events for bookmark support.
        """
        # auto bookmark store
        if event in (STOP, USER_END):
            if item.mode == 'file' and not item.variants and \
                   not item.subitems and item.elapsed:
                item.store_info('autobookmark_resume', item.elapsed)
            else:
                log.info('auto-bookmark not supported for this item')
            return False

        # auto bookmark delete
        if event == PLAY_END:
            item.delete_info('autobookmark_resume')
            return False

        # bookmark the current time into a file
        if event == STORE_BOOKMARK:
            bookmarkfile = self.get_bookmarkfile(item.filename)

            handle = open(bookmarkfile,'a+')
            handle.write(str(item.elapsed))
            handle.write('\n')
            handle.close()
            eventhandler.post(Event(OSD_MESSAGE, arg='Added Bookmark'))
            return True

        return False
