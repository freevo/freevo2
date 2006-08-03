# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directory.py - Directory handling
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
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
import stat
import copy
import logging
import time

# kaa imports
import kaa
import kaa.notifier
import kaa.beacon
from kaa.weakref import weakref

# freevo imports
import config
import util

import menu
import plugin
import fxditem

from menu import Item, Files, Action, ActionItem
from playlist import Playlist
from event import *

from gui.windows import InputBox, MessageBox, ProgressBox

# get logging object
log = logging.getLogger()

# variables for 'configure' submenu
all_variables = [('DIRECTORY_SORT_BY_DATE', _('Directory Sort By Date'),
                  _('Sort directory by date and not by name.'), False),

                 ('DIRECTORY_AUTOPLAY_SINGLE_ITEM',
                  _('Directory Autoplay Single Item'),
                  _('Don\'t show directory if only one item exists and ' \
                    'auto-select the item.'), False),

                 ('DIRECTORY_SMART_SORT', _('Directory Smart Sort'),
                  _('Use a smarter way to sort the items.'), False),

                 ('DIRECTORY_USE_MEDIAID_TAG_NAMES',
                  _('Use MediaID Tag Names'),
                  _('Use the names from the media files tags as display ' \
                    'name.'), False),

                 ('DIRECTORY_REVERSE_SORT', _('Directory Reverse Sort'),
                  _('Show the items in the list in reverse order.'), False),

                 ('DIRECTORY_AUDIO_FORMAT_STRING', '', '', False),

                 ('DIRECTORY_CREATE_PLAYLIST', _('Directory Create Playlist'),
                  _('Handle the directory as playlist. After one file is '\
                    'played, the next one will be started.'), True) ,

                 ('DIRECTORY_ADD_PLAYLIST_FILES',
                  _('Directory Add Playlist Files'),
                  _('Add playlist files to the list of items'), True) ,

                 ('DIRECTORY_ADD_RANDOM_PLAYLIST',
                  _('Directory Add Random Playlist'),
                  _('Add an item for a random playlist'), True) ,

                 ('DIRECTORY_AUTOPLAY_ITEMS', _('Directory Autoplay Items'),
                  _('Autoplay the whole directory (as playlist) when it '\
                    'contains only files and no directories' ), True)]



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
    def __init__(self, directory, parent, name = '', display_type = None,
                 add_args = None):
        Playlist.__init__(self, parent=parent, display_type=display_type)
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
            self.name = Unicode(name)

        if add_args == None and hasattr(parent, 'add_args'):
            add_args = parent.add_args
        self.add_args = add_args

        if self['show_all_items']:
            self.display_type = None

        # set tv to video now
        if self.display_type == 'tv':
            display_type = 'video'

        # set directory variables to default
        self.all_variables = copy.copy(all_variables)

        # Check mimetype plugins if they want to add something
        for p in plugin.mimetype(display_type):
            self.all_variables += p.dirconfig(self)

        # set the variables to the default values
        for var in self.all_variables:
            if hasattr(parent, var[0]):
                setattr(self, var[0], getattr(parent, var[0]))
            elif hasattr(config, var[0]):
                setattr(self, var[0], getattr(config, var[0]))
            else:
                setattr(self, var[0], False)

        self.modified_vars = []

        # Check mimetype plugins if they want to add something
        for p in plugin.mimetype(display_type):
            p.dirinfo(self)

        if self.DIRECTORY_SORT_BY_DATE == 2 and self.display_type != 'tv':
            self.DIRECTORY_SORT_BY_DATE = 0

        # special database key for extra arguments
        display_type = display_type or 'all'
        self._dbprefix = 'freevo:directory:%s' % display_type


    def __is_type_list_var(self, var):
        """
        return if this variable to be saved is a type_list
        """
        for v,n,d, type_list in self.all_variables:
            if v == var:
                return type_list
        return False


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
            if not self.info.scanned() or \
                   self.info.get('%s:mtime' % self._dbprefix) != self.info.get('mtime'):
                # create information
                log.info('create metainfo for %s', self.dir)
                listing = kaa.beacon.query(parent=self.info).get(filter='extmap')
                num_play_items = 0
                for p in plugin.mimetype(display_type):
                    num_play_items += p.count(self, listing)
                self['%s:play' % self._dbprefix] = num_play_items
                self['%s:dir' % self._dbprefix] = len(listing.get('beacon:dir'))
                if self.info.scanned():
                    # FIXME: put this somewhere into beacon as a plugin
                    self.info['%s:mtime' % self._dbprefix] = self.info.get('mtime')

            if key == 'num_items':
                return self.info['%s:play' % self._dbprefix] + \
                       self.info['%s:dir' % self._dbprefix]

            if key == 'num_play_items':
                return self.info['%s:play' % self._dbprefix]

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

        return Item.__getitem__(self, key)


    # eventhandler for this item
    def eventhandler(self, event):
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

            # delete current menu (showing the directory)
            self.get_menustack().back_one_menu(False)

            # create a new directory item
            d = DirItem(self.dir, self.parent, self.name, type, self.add_args)
            # deactivate autoplay
            d.DIRECTORY_AUTOPLAY_SINGLE_ITEM = False
            # replace current item with the new one
            self.replace(d)
            # build new dir (this will add a new menu)
            d.browse()
            # show message
            OSD_MESSAGE.post('%s view' % type)
            return True

        if event == PLAY_START and self.item_menu and \
               event.arg in self.item_menu.choices:
            # update selection and pass the event to playlist after that
            self.item_menu.select(event.arg)

        return Playlist.eventhandler(self, event)


    # ======================================================================
    # actions
    # ======================================================================

    def actions(self):
        """
        return a list of actions for this item
        """
        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        browse = Action(_('Browse directory'), self.browse)
        play = Action(_('Play all files in directory'), self.play)

        if self.info['num_%s_items' % display_type]:
            if display_type in self.DIRECTORY_AUTOPLAY_ITEMS and \
                   not self['num_dir_items']:
                items = [ play, browse ]
            else:
                items = [ browse, play ]
        else:
            items = [ browse ]

        if self.info['num_%s_items' % display_type]:
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
	    MessageBox(_('Directory does not exist')).show()
            return
        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'
        pl = Playlist(playlist = [ (self.dir, recursive) ], parent = self,
                      display_type=display_type, random=random)
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
	    MessageBox(_('Directory does not exist')).show()
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
            d = DirItem(item, self, display_type = self.display_type)
            dir_items.append(d)

        # remember listing
        self.listing = listing

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
        if self.DIRECTORY_SMART_SORT:
            dir_items.sort(lambda l, o: smartsort(l.dir,o.dir))
        else:
            dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))

        # sort playlist
        pl_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))

        # sort normal items
        if self.DIRECTORY_SORT_BY_DATE:
            play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                                  o.sort('date').upper()))
        elif self['%s_advanced_sort' % display_type]:
            play_items.sort(lambda l, o: cmp(l.sort('advanced').upper(),
                                                  o.sort('advanced').upper()))
        else:
            play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                                  o.sort().upper()))

        if self['%s:dir' % self._dbprefix] != len(dir_items):
            self['%s:dir' % self._dbprefix] = len(dir_items)
        if self['%s:play' % self._dbprefix] != len(play_items) + len(pl_items):
            self['%s:play' % self._dbprefix] = len(play_items) + len(pl_items)

        if self.DIRECTORY_REVERSE_SORT:
            dir_items.reverse()
            play_items.reverse()
            pl_items.reverse()

        # delete pl_items if they should not be displayed
        if self.display_type and not self.display_type in \
               self.DIRECTORY_ADD_PLAYLIST_FILES:
            pl_items = []

        # add all playable items to the playlist of the directory
        # to play one files after the other
        if not self.display_type or self.display_type in \
               self.DIRECTORY_CREATE_PLAYLIST:
            self.playlist = play_items


        # build a list of all items
        items = dir_items + pl_items + play_items

        # random playlist (only active for audio)
        if self.display_type and self.display_type in \
               self.DIRECTORY_ADD_RANDOM_PLAYLIST \
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
        item_menu.autoselect = self.DIRECTORY_AUTOPLAY_SINGLE_ITEM
        self.pushmenu(item_menu)
        self.item_menu = weakref(item_menu)


    # ======================================================================
    # configure submenu
    # ======================================================================


    def configure_set_name(self, name):
        """
        return name for the configure menu
        """
        if name in self.modified_vars:
            if getattr(self, name):
                return 'ICON_RIGHT_ON_' + _('on')
            else:
                return 'ICON_RIGHT_OFF_' + _('off')
        else:
            return 'ICON_RIGHT_AUTO_' + _('auto')


    def configure_set_var(self, var):
        """
        Update the variable in var and change the menu. This function is used
        by 'configure'
        """

        # get current value, None == no special settings
        if var in self.modified_vars:
            if self.__is_type_list_var(var):
                if getattr(self, var):
                    current = 1
                else:
                    current = 0
            else:
                current = getattr(self, var)
        else:
            current = None

        # get the max value for toggle
        max = 1

        # switch from no settings to 0
        if current == None:
            self.modified_vars.append(var)
            if self.__is_type_list_var(var):
                setattr(self, var, [])
            else:
                setattr(self, var, 0)

        # inc variable
        elif current < max:
            if self.__is_type_list_var(var):
                setattr(self, var, [self.display_type])
            else:
                setattr(self, var, current+1)

        # back to no special settings
        elif current == max:
            if self.parent and hasattr(self.parent, var):
                setattr(self, var, getattr(self.parent, var))
            if hasattr(config, var):
                setattr(self, var, getattr(config, var))
            else:
                setattr(self, var, False)
            self.modified_vars.remove(var)

        # change name
        item = self.get_menustack().get_selected()
        item.name = item.name[:item.name.find(u'\t') + 1] + \
                    self.configure_set_name(var)

        # BEACON_FIXME: store in db
        
        # rebuild menu
        self.get_menustack().refresh(True)


    def configure_set_display_type(self):
        """
        change display type from specific to all
        """
        if self.display_type:
            self['show_all_items'] = True
            self.display_type = None
            name = u'\tICON_RIGHT_ON_' + _('on')
        else:
            self['show_all_items'] = False
            self.display_type = self.parent.display_type
            name = u'\tICON_RIGHT_OFF_' + _('off')

        # change name
        item = self.get_menustack().get_selected()
        item.name = item.name[:item.name.find(u'\t')]  + name

        # rebuild menu
        self.get_menustack().refresh(True)


    def configure(self):
        """
        show the configure dialog for folder specific settings
        """
        items = []
        for i, name, descr, type_list in self.all_variables:
            if name == '':
                continue
            name += '\t'  + self.configure_set_name(i)
            action = ActionItem(name, self, self.configure_set_var, descr)
            action.parameter(var=i)
            items.append(action)

        if self.parent and self.parent.display_type:
            if self.display_type:
                name = u'\tICON_RIGHT_OFF_' + _('off')
            else:
                name = u'\tICON_RIGHT_ON_' + _('on')

            descr = _('Show video, audio and image items in this directory')
            action = ActionItem(_('Show all kinds of items') + name, self,
                                self.configure_set_display_type, descr)
            action.parameter(var=i)
            items.append(action)

        self.get_menustack().delete_submenu(False)
        m = menu.Menu(_('Configure'), items)
        m.table = (80, 20)
        self.pushmenu(m)
