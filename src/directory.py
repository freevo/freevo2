# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directory.py - Directory handling
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2007 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
import stat
import copy
import logging
import time

# kaa imports
import kaa
import kaa.notifier
import kaa.beacon
from kaa.weakref import weakref
from kaa.strutils import str_to_unicode

# freevo imports
import config
import util

import menu
import plugin
import fxditem

from menu import Item, Files, Action, ActionItem
from playlist import Playlist
from event import *

from application import MessageWindow

# get logging object
log = logging.getLogger()

# variables for 'configure' submenu
_variables = [
    ('SORT_BY_DATE', _('Sort By Date'),
     _('Sort directory by date and not by name.')),
    ('AUTOPLAY_SINGLE_ITEM', _('Autoplay Single Item'),
     _('Don\'t show directory if only one item exists and auto select the item.')),
    ('USE_MEDIADB_NAMES', _('Use Tag Names'),
     _('Use the names from the media files tags as display name.')),
    ('REVERSE_SORT', _('Reverse Sort'),
     _('Show the items in the list in reverse order.')),
    ('CREATE_PLAYLIST', _('Create Playlist'),
     _('Handle the directory as playlist and play the next item when ine is done.')) ,
    ('AUTOPLAY_ITEMS', _('Autoplay Items'),
     _('Autoplay the whole directory (as playlist) when it contains only files.')),
    ('HIDE_PLAYED', _('Hide Played Items'),
     _('Hide items already played.'))]


kaa.beacon.register_file_type_attrs('dir',
    freevo_num_items = (dict, kaa.beacon.ATTR_SIMPLE),
    freevo_sort_by_date = (str, kaa.beacon.ATTR_SIMPLE),
    freevo_autoplay_single_item = (str, kaa.beacon.ATTR_SIMPLE),
    freevo_use_mediadb_names = (str, kaa.beacon.ATTR_SIMPLE),
    freevo_reverse_sort = (str, kaa.beacon.ATTR_SIMPLE),
    freevo_create_playlist = (str, kaa.beacon.ATTR_SIMPLE),
    freevo_autoplay_items = (str, kaa.beacon.ATTR_SIMPLE),
    freevo_hide_played = (str, kaa.beacon.ATTR_SIMPLE),
)

def smartsort(x,y):
    """
    Compares strings after stripping off 'The' and 'A' to be 'smarter'
    Also obviously ignores the full path when looking for 'The' and 'A'
    """
    m = os.path.basename(x)
    n = os.path.basename(y)

    for word in ('The', 'A'):
        word += ' '
        if m.find(word) == 0:
            m = m.replace(word, '', 1)
        if n.find(word) == 0:
            n = n.replace(word, '', 1)

    return cmp(m.upper(),n.upper()) # be case insensitive


def find_start_string(s1, s2):
    """
    Find similar start in both strings
    """
    ret = ''
    tmp = ''
    while True:
        if len(s1) < 2 or len(s2) < 2:
            return ret
        if s1[0] == s2[0]:
            tmp += s2[0]
            if s1[1] in (u' ', u'-', u'_', u',', u':', '.') and \
               s2[1] in (u' ', u'-', u'_', u',', u':', '.'):
                ret += tmp + u' '
                tmp = ''
            s1 = s1[1:].lstrip(u' -_,:.')
            s2 = s2[1:].lstrip(u' -_,:.')
        else:
            return ret


def remove_start_string(string, start):
    """
    remove start from the beginning of string.
    """
    start = start.replace(u' ', '')
    for i in range(len(start)):
        string = string[1:].lstrip(' -_,:.')

    return string[0].upper() + string[1:]


class DirItem(Playlist):
    """
    class for handling directories
    """
    def __init__(self, directory, parent, name = '', type = None,
                 add_args = None):
        Playlist.__init__(self, parent=parent, type=type)
        self.type = 'dir'
        self.item_menu  = None

        if not isinstance(directory, kaa.beacon.Item):
            log.warning('filename as directory is deprecated')
            directory = kaa.beacon.get(directory)

        self.set_url(directory)

        self.files = Files()
        if directory.get('read_only'):
            self.files.read_only = True
        self.files.append(directory)

        # FIXME: remove this
        self.dir = directory.filename
        self.url = directory.filename

        if name:
            self.name = str_to_unicode(name)

        if add_args == None and hasattr(parent, 'add_args'):
            add_args = parent.add_args
        self.add_args = add_args

        if self['show_all_items']:
            # FIXME: no way to set this
            self.display_type = None

        # set tv to video now
        if self.display_type == 'tv':
            type = 'video'

        # Check mimetype plugins if they want to add something
        for p in plugin.mimetype(type):
            p.dirinfo(self)


    def __getitem__(self, key):
        """
        return the specific attribute
        """
        if key == 'type':
            return _('Directory')

        if key.startswith('num_'):
            # special keys to get number of playable items or the
            # sum of all items in that directory
            display_type = self.display_type
            if self.display_type == 'tv':
                display_type = 'video'

            # get number of items info from beacon
            num_items_all = self.info.get('freevo_num_items') or {}
            num_items = num_items_all.get(display_type)
            if num_items and num_items[0] != self.info.get('mtime'):
                num_items = None

            if not num_items:
                log.info('create metainfo for %s', self.dir)
                listing = kaa.beacon.query(parent=self.info).get(filter='extmap')
                num_items = [ self.info.get('mtime'), 0 ]
                for p in plugin.mimetype(display_type):
                    num_items[1] += p.count(self, listing)
                num_items.append(len(listing.get('beacon:dir')))
                if self.info.scanned():
                    num_items_all[display_type] = num_items
                    self.info['freevo_num_items'] = copy.copy(num_items_all)

            if key == 'num_items':
                return num_items[1] + num_items[2]

            if key == 'num_play_items':
                return num_items[1]

            if key == 'num_dir_items':
                return num_items[2]

        if key in ( 'freespace', 'totalspace' ):
            space = getattr(util, key)(self.dir) / 1000000
            if space > 1000:
                space='%s,%s' % (space / 1000, space % 1000)
            return space

        if key == 'length':
            try:
                length = int(self.info['length'])
            except ValueError:
                return self.info['length']
            except:
                try:
                    length = int(self.length)
                except:
                    return ''
            if length == 0:
                return ''
            if length / 3600:
                return '%d:%02d:%02d' % ( length / 3600, (length % 3600) / 60,
                                          length % 60)
            else:
                return '%d:%02d' % (length / 60, length % 60)

        if key.startswith('config:'):
            value = self.info.get('tmp:%s' % key[7:])
            if value is not None:
                return value
            value = self.info.get('freevo_%s' % key[7:])
            if value and not value == 'auto':
                return value == 'yes'
            if isinstance(self.parent, DirItem):
                return self.parent[key]
            value = getattr(config, 'DIRECTORY_%s' % key[7:].upper(), False)
            if not isinstance(value, (list, tuple)):
                if value in (1, True):
                    return True
                if value in (0, False):
                    return False
                return value
            if self.display_type == 'tv':
                return 'video' in value
            return self.display_type in value

        return Item.__getitem__(self, key)


    # eventhandler for this item
    def eventhandler(self, event):

        if self.item_menu == None:
            return Playlist.eventhandler(self, event)

        if event == DIRECTORY_CHANGE_DISPLAY_TYPE:
            possible = [ ]

            for p in plugin.get('mimetype'):
                for t in p.display_type:
                    if not t in possible:
                        possible.append(t)

            try:
                pos = possible.index(self.display_type)
                type = possible[(pos+1) % len(possible)]
            except (IndexError, ValueError), e:
                return Playlist.eventhandler(self, event)

            self.display_type = type
            self['tmp:autoplay_single_item'] = False
            self.item_menu.autoselect = False
            self.browse(update=True)
            OSD_MESSAGE.post('%s view' % type)
            return True

        if event == DIRECTORY_TOGGLE_HIDE_PLAYED:
            self['tmp:hide_played'] = not self['config:hide_played']
            self['tmp:autoplay_single_item'] = False
            self.item_menu.autoselect = False
            self.browse(update=True)
            if self['config:hide_played']:
                OSD_MESSAGE.post('Hide played items')
            else:
                OSD_MESSAGE.post('Show all items')

        return Playlist.eventhandler(self, event)


    # ======================================================================
    # actions
    # ======================================================================

    def actions(self):
        """
        return a list of actions for this item
        """
        browse = Action(_('Browse directory'), self.browse)
        play = Action(_('Play all files in directory'), self.play)

        if self['num_items']:
            if self['config:autoplay_items'] and not self['num_dir_items']:
                items = [ play, browse ]
            else:
                items = [ browse, play ]
        else:
            items = [ browse ]

        if self.info['num_items']:
            a = Action(_('Random play all items'), self.play)
            a.parameter(random=True)
            items.append(a)

        if self['num_dir_items']:
            a = Action(_('Recursive random play all items'), self.play)
            a.parameter(random=True, recursive=True)
            items.append(a)
            a = Action(_('Recursive play all items'), self.play)
            a.parameter(recursive=True)
            items.append(a)

        a = Action(_('Configure directory'), self.configure, 'configure')
        items.append(a)

        return items



    def play(self, random=False, recursive=False):
        """
        play directory
        """
        # FIXME: add password checking here
        if not os.path.exists(self.dir):
	    MessageWindow(_('Directory does not exist')).show()
            return
        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        query = kaa.beacon.query(parent=self.info, recursive=recursive)
        pl = Playlist(playlist = query, parent = self,
                      type=display_type, random=random)
        pl.play()

        # Now this is ugly. If we do nothing 'pl' will be deleted by the
        # garbage collector, so we have to store it somehow
        self.__pl_for_gc = pl
        return


    def browse(self, update=False, authstatus=0):
        """
        build the items for the directory
        """
        # FIXME: check for password

        self.playlist   = []
        play_items = []
        dir_items  = []
        pl_items   = []

        if update:
            # Delete possible skin settings
            # FIXME: This is a very bad handling, maybe signals?
            if hasattr(self.item_menu, 'skin_default_has_description'):
                del self.item_menu.skin_default_has_description
            if hasattr(self.item_menu, 'skin_default_no_images'):
                del self.item_menu.skin_default_no_images
            if hasattr(self.item_menu, 'skin_force_text_view'):
                del self.item_menu.skin_force_text_view

        elif not os.path.exists(self.dir):
            # FIXME: better handling!!!!!
	    MessageWindow(_('Directory does not exist')).show()
            return

        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        if not update:
            self.query = kaa.beacon.query(parent=self.info)
            self.query.signals['changed'].connect_weak(self.browse, update=True)
            self.query.monitor()
        listing = self.query.get(filter='extmap')

        #
        # build items
        #
        # build play_items, pl_items and dir_items
        for p in plugin.mimetype(display_type):
            for i in p.get(self, listing):
                if i.type == 'playlist':
                    pl_items.append(i)
                elif i.type == 'dir':
                    dir_items.append(i)
                else:
                    play_items.append(i)

        # normal DirItems
        for item in listing.get('beacon:dir'):
            d = DirItem(item, self, type = self.display_type)
            dir_items.append(d)

        # remember listing
        self.listing = listing

        # handle hide_played
        if self['config:hide_played']:
            play_items = [ p for p in play_items if not p.info.get('last_played') ]

        # remove same beginning from all play_items
        substr = ''
        if len(play_items) > 4 and len(play_items[0].name) > 5:
            substr = play_items[0].name[:-5].lower()
            for i in play_items[1:]:
                if len(i.name) > 5:
                    substr = find_start_string(i.name.lower(), substr)
                    if not substr or len(substr) < 10:
                        break
                else:
                    break
            else:
                for i in play_items:
                    i.name = remove_start_string(i.name, substr)


        #
        # sort all items
        #

        # sort directories
        if config.DIRECTORY_SMART_SORT:
            dir_items.sort(lambda l, o: smartsort(l.dir,o.dir))
        else:
            dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))

        # sort playlist
        pl_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))

        # sort normal items
        sort_by_date = self['config:sort_by_date']
        if sort_by_date == 2 and not self.display_type == 'tv':
            sort_by_date = False
        if sort_by_date:
            play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                             o.sort('date').upper()))
        else:
            play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                             o.sort().upper()))

        # update num_items information if needed
        num_items_all = self.info.get('freevo_num_items') or {}
        num_items = num_items_all.get(display_type)
        if num_items and (num_items[1] != len(play_items) + len(pl_items) or \
                          num_items[2] != len(dir_items)):
            num_items[1] = len(play_items) + len(pl_items)
            num_items[2] = len(dir_items)
            self.info['freevo_num_items'] = copy.copy(num_items_all)

        if self['config:reverse_sort']:
            dir_items.reverse()
            play_items.reverse()
            pl_items.reverse()

        # delete pl_items if they should not be displayed
        if self.display_type and not self.display_type in \
               config.DIRECTORY_ADD_PLAYLIST_FILES:
            pl_items = []

        # add all playable items to the playlist of the directory
        # to play one files after the other
        if self['config:create_playlist']:
            self.playlist = play_items


        # build a list of all items
        items = dir_items + pl_items + play_items

        # random playlist (only active for audio)
        if self.display_type and self.display_type in \
               config.DIRECTORY_ADD_RANDOM_PLAYLIST \
               and len(play_items) > 1:
            pl = Playlist(_('Random playlist'), play_items, self,
                          random=True)
            pl.autoplay = True
            items = [ pl ] + items


        #
        # action
        #

        if update:
            if self.item_menu:
                self.item_menu.set_items(items)
            return

        # normal menu build
        item_menu = menu.Menu(self.name, items, type = display_type)
        item_menu.autoselect = self['config:autoplay_single_item']
        self.pushmenu(item_menu)
        self.item_menu = weakref(item_menu)

    # ======================================================================
    # configure submenu
    # ======================================================================


    def configure_get_status(self, var):
        """
        return name for the configure menu
        """
        value = self.info.get('freevo_%s' % var.lower())
        if value == 'yes':
            return 'ICON_RIGHT_ON_' + _('on')
        if value == 'no':
            return 'ICON_RIGHT_OFF_' + _('off')
        return 'ICON_RIGHT_AUTO_' + _('auto')


    def configure_set_var(self, var):
        """
        Update the variable in var and change the menu. This function is used
        by 'configure'
        """
        dbvar = 'freevo_%s' % var.lower()
        current = self.info.get(dbvar) or 'auto'
        if current == 'auto':
            self.info[dbvar] = 'yes'
        elif current == 'yes':
            self.info[dbvar] = 'no'
        else:
            self.info[dbvar] = 'auto'

        # change name
        item = self.get_menustack().get_selected()
        item.name = item.name[:item.name.find(u'\t') + 1] + \
                    self.configure_get_status(var)

        # rebuild menu
        self.get_menustack().refresh(True)


    def configure(self):
        """
        show the configure dialog for folder specific settings
        """
        items = []
        for i, name, descr in _variables:
            name += '\t'  + self.configure_get_status(i)
            action = ActionItem(name, self, self.configure_set_var, descr)
            action.parameter(var=i)
            items.append(action)
        self.get_menustack().delete_submenu(False)
        m = menu.Menu(_('Configure'), items)
        m.table = (80, 20)
        self.pushmenu(m)
