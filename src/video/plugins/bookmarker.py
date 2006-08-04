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
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Aubin Paul <aubin@outlyer.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
import logging
import kaa.metadata
import kaa.beacon

# freevo imports
import sysconfig
import util

from menu import Action, Menu, ItemPlugin
from event import *

# the logging object
log = logging.getLogger()

# variable to store the auto resume
RESUME = 'autobookmark_resume'

kaa.beacon.register_file_type_attrs('video',
    autobookmark_resume = (int, kaa.beacon.ATTR_SIMPLE))

class PluginInterface(ItemPlugin):
    """
    class to handle auto bookmarks
    """

    def __init__(self):
        ItemPlugin.__init__(self)
        self._ignore_end = False
        
    def get_bookmarkfile(self, filename):
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
        if item.type == 'dir' or item.type == 'playlist' or item.iscopy:
            # only works for video items
            return []
        actions = []
        if item[RESUME]:
            actions.append(Action(_('Resume playback'), self.resume))
        if item.mode == 'file' and not item.subitems \
               and os.path.exists(self.get_bookmarkfile(item.filename)):
            actions.append(Action(_('Bookmarks'), self.bookmark_menu))
        return actions


    def resume(self, item):
        """
        Resume playback
        """
        t = max(0, item[RESUME] - 10)
        info = kaa.metadata.parse(item.filename)
        if hasattr(info, 'seek') and t:
            mplayer_options = '-sb %s' % info.seek(t)
        else:
            mplayer_options = '-ss %s' % t
        item.get_menustack().delete_submenu()
        item.play(mplayer_options = mplayer_options)


    def bookmark_menu(self, item):
        """
        Bookmark list
        """
        bookmarkfile = self.get_bookmarkfile(item.filename)
        item.get_menustack().delete_submenu(False)

        items = []
        for line in util.readfile(bookmarkfile):
            copy = item.copy()

            sec  = int(line)
            hour = int(sec/3600)
            min  = int((sec-(hour*3600))/60)
            sec  = int(sec%60)
            time = '%0.2d:%0.2d:%0.2d' % (hour,min,sec)

            # set a new title
            copy.name = Unicode(_('Jump to %s') % (time))
            if not copy.mplayer_options:
                copy.mplayer_options = ''
            copy.mplayer_options += ' -ss %s' % time
            items.append(copy)

        if items:
            moviemenu = Menu(item.name, items)
            item.pushmenu(moviemenu)


    def eventhandler(self, item, event):
        """
        Handle video events for bookmark support.
        """
        # auto bookmark store
        if event == STOP:
            if item.mode == 'file' and not item.subitems and item.elapsed:
                # this will store in kaa.beacon
                item[RESUME]= item.elapsed
                self._ignore_end = True
            else:
                log.info('auto-bookmark not supported for this item')
            return False

        # auto bookmark delete
        if event == PLAY_END:
            if self._ignore_end:
                self._ignore_end = False
            else:
                item[RESUME] = None
            return False

        # bookmark the current time into a file
        if event == STORE_BOOKMARK:
            bookmarkfile = self.get_bookmarkfile(item.filename)

            handle = open(bookmarkfile,'a+')
            handle.write(str(item.elapsed))
            handle.write('\n')
            handle.close()
            OSD_MESSAGE.post(_('Added Bookmark'))
            return True

        return False
