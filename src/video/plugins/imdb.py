# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# imdb.py - Plugin for IMDB support
# -----------------------------------------------------------------------------
# $Id$
#
# Plugin to receive IMDB information for a video file.
#
# Todo:  - function to add to an existing fxd file
#        - DVD/VCD support
#        - replace threads with code from pywebinfo
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

# python import
import os
import re
import time

# kaa imports
import kaa.notifier

# freevo imports
import config

from menu import Action, ActionItem, Menu, ItemPlugin
from util.fxdimdb import FxdImdb, makeVideo, makePart, point_maker
from gui.windows import WaitBox, MessageBox
from util import htmlenties2txt

# shortcut for the actions
SHORTCUT = 'imdb_search_or_cover_search'


class PluginInterface(ItemPlugin):
    """
    Add IMDB informations for video items.

    activate with plugin.activate('video.imdb')
    You can also set imdb_search on a key (e.g. '1') by setting
    EVENTS['menu']['1'] = Event(MENU_CALL_ITEM_ACTION,
           arg='imdb_search_or_cover_search')
    """
    def __init__(self, license=None):
        """
        Init the plugin.
        """
        if not config.USE_NETWORK:
            self.reason = 'no network'
            return
        ItemPlugin.__init__(self)


    def __imdb_get_disc_searchstring(self, item):
        """
        Get search string for a disc.
        """
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
        """
        Possible actions for the given item.
        """
        name = ''
        if item.type == 'video' and \
               (not item.files or not item.files.fxd_file):
            if item.mode == 'file' or (item.mode in ('dvd', 'vcd') and \
                                       item.info.has_key('tracks') and not \
                                       item.media):
                name = _('Search IMDB for this file')
                dset = False
            elif item.mode in ('dvd', 'vcd') and item.info.has_key('tracks'):
                s = self.__imdb_get_disc_searchstring(item)
                if s:
                    name = _('Search IMDB for [%s]') % s
                    dset = True

        if item.type == 'dir' and item.media and \
               item.media.mountdir.find(item.dir) == 0:
            s = self.__imdb_get_disc_searchstring(item)
            if s:
                name = _('Search IMDB for [%s]') % s
                dset = True
        if name:
            # found am action
            a = Action(name, self.imdb_search, SHORTCUT)
            a.parameter(dset)
            return [ a ]
        return []

            
    def imdb_search(self, item, disc_set):
        """
        Search imdb for the item
        """
        # go back to the item menu
        item.show_menu(False)

        # get fxd object
        fxd = FxdImdb()

        # show popup while doing stuff
        box = WaitBox(text=_('searching IMDB...'))
        box.show()

        if disc_set:
            searchstring = item.media.label
        else:
            searchstring = item.name

        # start search in thread
        thread = kaa.notifier.Thread(fxd.guessImdb, searchstring, disc_set)
        thread.signals['completed'].connect(self.parse_results, item, disc_set, box)
        thread.signals['exception'].connect(self.handle_exception, item, box)
        thread.start()
            

    def handle_exception(self, exception, item, box):
        """
        Exception while getting data from IMDB.
        """
        box.destroy()
        MessageBox(exception).show()
        item.show_menu()

        
    def parse_results(self, results, item, disc_set, box):
        """
        Handle IMDB search results. This function is called after the search
        thread is finished.
        """
        items = []
        for id, name, year, type in results:
            name = '%s (%s, %s)' % (htmlenties2txt(name), year, type)
            a = ActionItem(name, item, self.download)
            a.parameter(id, disc_set)
            items.append(a)

        # delete search box
        box.destroy()

        if config.IMDB_AUTOACCEPT_SINGLE_HIT and len(items) == 1:
            # get data from result
            items[0]()
            return

        if items:
            # show possible entries
            item.pushmenu(Menu(_('IMDB Query'), items))
            return

        # show error message
        MessageBox(text=_('No information available from IMDB')).show()
        return

        
    def download(self, item, id, disc_set):
        """
        Download IMDB information.
        """
        fxd = FxdImdb()
        
        box = WaitBox(text=_('getting data...'))
        box.show()

        # if this exists we got a cdrom/dvdrom
        if item.media and item.media.devicename: 
            devicename = item.media.devicename
        else:
            devicename = None

        # start download in thread
        thread = kaa.notifier.Thread(fxd.setImdbId, id)
        thread.signals['completed'].connect(self.save, item, fxd, box, disc_set, devicename)
        thread.signals['exception'].connect(self.handle_exception, item, box)
        thread.start()
        

    def save(self, result, item, fxd, box, disc_set, devicename):
        """
        Create fxd file for the item.
        """
        if disc_set:
            fxd.setDiscset(devicename, None)
        else:
            if item.subitems:
                for i in range(len(item.subitems)):
                    file = os.path.basename(item.subitems[i].filename)
                    video = makeVideo('file', 'f%s' % i, file,
                                      device=devicename)
                    fxd.setVideo(video)
            else:
                file = os.path.basename(item.filename)
                video = makeVideo('file', 'f1', file, device=devicename)
                fxd.setVideo(video)
            fxd.setFxdFile(os.path.splitext(item.filename)[0])

        fxd.writeFxd()
        item.show_menu()
        box.destroy()
