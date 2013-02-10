# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directory.py - Directory handling
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, 2003-2012 Dirk Meyer, et al.
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

__all__ = [ 'Directory' ]

# python imports
import os
import logging

# kaa imports
import kaa
import kaa.beacon
from kaa.weakref import weakref

# freevo imports
import api as freevo

# get logging object
log = logging.getLogger()

# get config object directory
config = freevo.config.directory

def _find_start_string(s1, s2):
    """
    Find similar start in both strings
    """
    ret = u''
    tmp = u''
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
            continue
        return ret


def _remove_start_string(string, start):
    """
    remove start from the beginning of string.
    """
    start = start.replace(u' ', '')
    for i in range(len(start)):
        string = string[1:].lstrip(' -_,:.')
    return string[0].upper() + string[1:]


class Directory(freevo.Playlist):
    """
    class for handling directories
    """
    type = 'directory'

    CACHED_ATTRIBUTES = \
        ['hide_played', 'sort_method', 'autoplay_single_item', 'autoplay_items', 'isplaylist' ]
    CACHED_ATTRIBUTES_MTIME = \
        ['num_items_dict']

    def __init__(self, directory, parent, name = '', type = None):
        # store type as menu_type and go on handling it as media_type
        # with tv replaced by video. Only Directory has a difference between
        # media_type and menu_type with the extra tv value. This is needed
        # to show a tv based skin when browsing a dir from the tv plugin.
        self.menu_type = type
        if type == 'tv':
            type = 'video'
        super(Directory, self).__init__(parent=parent, type=type)
        self.item_menu  = None
        self.set_url(directory)
        if name:
            self.name = kaa.str_to_unicode(name)
        if self['show_all_items']:
            # FIXME: no way to set this
            self.media_type = None
        self._beacon_query = None

    @kaa.coroutine(policy=kaa.POLICY_SINGLETON)
    def __calculate_num_items(self, type):
        """
        Set the number of items in the directory based on the listing.
        """
        if self.media_type:
            type += '_' + self.media_type
        if self.num_items_dict:
            num_items = self.num_items_dict.get(type)
            if num_items is not None:
                yield num_items
        log.info('create metainfo for %s', self.filename)
        listing = yield kaa.beacon.query(parent=self.info)
        listing = listing.get(filter='extmap')
        mediatype = ''
        if self.media_type:
            media_type = '_%s' % self.media_type
        num = 0
        for p in freevo.MediaPlugin.plugins(self.media_type):
            num += p.count(self, listing)
        if not self.num_items_dict:
            self.num_items_dict = {}
        self.num_items_dict['play%s' % media_type] = num
        self.num_items_dict['dir%s' % media_type] = len(listing.get('beacon:dir'))
        self.num_items_dict['all%s' % media_type] = num + len(listing.get('beacon:dir'))
        self.num_items_dict = self.num_items_dict
        self.menustack.refresh()

    @property
    def num_items(self):
        progress = self.__calculate_num_items('all')
        if progress.finished:
            return progress.result

    @property
    def num_items_play(self):
        progress = self.__calculate_num_items('play')
        if progress.finished:
            return progress.result

    @property
    def num_items_dir(self):
        progress = self.__calculate_num_items('dir')
        if progress.finished:
            return progress.result

    @property
    def freespace(self):
        """
        Return free space in the directory in MB.
        Used by the generic Item.get function.
        """
        s = os.statvfs(self.filename)
        space = (s[os.statvfs.F_BAVAIL] * long(s[os.statvfs.F_BSIZE])) / 1000000
        space = space / 1000000
        if space > 1000:
            return '%s,%s' % (space / 1000, space % 1000)
        return space

    @property
    def totalspace(self):
        """
        Return total space in the directory in MB.
        Used by the generic Item.get function.
        """
        s = os.statvfs(self.filename)
        space = (s[os.statvfs.F_BLOCKS] * long(s[os.statvfs.F_BSIZE])) / 1000000
        if space > 1000:
            return '%s,%s' % (space / 1000, space % 1000)
        return space

    def actions(self):
        """
        return a list of actions for this item
        """
        browse = freevo.Action(_('Browse directory'), self.browse)
        play = freevo.Action(_('Play all files in directory'), self.play)
        if self.num_items:
            if self.config2value('autoplay_items') and not self.num_items_dir:
                items = [ play, browse ]
            else:
                items = [ browse, play ]
        else:
            items = [ browse ]
        if self.num_items:
            a = freevo.Action(_('Random play all items'), self.play)
            a.parameter(random=True)
            items.append(a)
        if self.num_items_dir:
            a = freevo.Action(_('Recursive random play all items'), self.play)
            a.parameter(random=True, recursive=True)
            items.append(a)
            a = freevo.Action(_('Recursive play all items'), self.play)
            a.parameter(recursive=True)
            items.append(a)
        return items

    @kaa.coroutine()
    def play(self, random=False, recursive=False):
        """
        play directory
        """
        if not os.path.exists(self.filename):
	    freevo.MessageWindow(_('Directory does not exist')).show()
            return
        items = yield kaa.beacon.query(parent=self.info, recursive=recursive)
        pl = freevo.Playlist(playlist=items, parent=self, type=self.media_type, random=random)
        pl.play()
        # Now this is ugly. If we do nothing 'pl' will be deleted by the
        # garbage collector, so we have to store it somehow
        self.__pl_for_gc = pl
        return

    @kaa.coroutine()
    def browse(self):
        """
        Show the items in the directory in the menu
        """
        if not os.path.exists(self.filename):
	    freevo.MessageWindow(_('Directory does not exist')).show()
            return
        self.item_menu = None
        self._beacon_query = yield kaa.beacon.query(parent=self.info)
        self._beacon_query.signals['changed'].connect_weak(self._get_items)
        self._beacon_query.monitor()
        item_menu = freevo.Menu(self.name, self._get_items(False), type = self.menu_type)
        item_menu.autoselect = self.config2value('autoplay_single_item')
        self.menustack.pushmenu(item_menu)
        self.item_menu = weakref(item_menu)

    def _get_items(self, update=True):
        """
        Get the items.
        """
        if not self.item_menu and update:
            # 'browse' not in the stack anymore
            self._beacon_query = None
            return
        play_items = []
        dir_items = []
        pl_items = []
        listing = self._beacon_query.get(filter='extmap')
        # build play_items, pl_items and dir_items
        for p in freevo.MediaPlugin.plugins(self.media_type):
            for i in p.get(self, listing):
                if i.type == 'playlist':
                    pl_items.append(i)
                elif i.type == 'directory':
                    dir_items.append(i)
                else:
                    play_items.append(i)
        for item in listing.get('beacon:dir'):
            # normal Directories
            dir_items.append(Directory(item, self, type = self.menu_type))
        # handle hide_played
        if self.config2value('hide_played'):
            play_items = [ p for p in play_items if not p.info.get('last_played') ]
        # remove same beginning from all play_items
        substr = u''
        if len(play_items) > 4 and len(play_items[0].name) > 5:
            substr = kaa.base.py3_str(play_items[0].name[:-5].lower())
            for i in play_items[1:]:
                if len(i.name) > 5:
                    substr = _find_start_string(kaa.base.py3_str(i.name.lower()), substr)
                    if not substr or len(substr) < 10:
                        break
                else:
                    break
            else:
                for i in play_items:
                    i.name = _remove_start_string(i.name, substr)
        def _sortfunc(m):
            return lambda l, o: cmp(l.sort(m), o.sort(m))
        # sort directories by name
        dir_items.sort(_sortfunc(self.config2value('sort_method')))
        # sort playlist by name or delete if they should not be displayed
        if self.menu_type and not self.menu_type in config.add_playlist_items.split(','):
            pl_items = []
        else:
            pl_items.sort(_sortfunc(self.config2value('sort_method')))
        play_items.sort(_sortfunc(self.config2value('sort_method')))
        if self.config2value('isplaylist'):
            self.set_items(play_items)
        # build a list of all items
        items = dir_items + pl_items + play_items
        # random playlist
        if self.menu_type and self.menu_type in config.add_random_playlist and len(play_items) > 1:
            pl = freevo.Playlist(
                _('Random playlist'), play_items, self, random=True, type=self.media_type)
            pl.autoplay = True
            pl.image = self.image
            pl.artist = self.get('artist')
            pl.album = self.get('album')
            items = [ pl ] + items
        if not self.item_menu:
            return items
        # update menu
        self.item_menu.set_items(items)

    def eventhandler(self, event):
        """
        Eventhandler for a directory item.
        """
        if self.item_menu == None:
            return super(Directory, self).eventhandler(event)
        if event == freevo.DIRECTORY_CHANGE_MENU_TYPE:
            possible = [ ]
            for p in freevo.MediaPlugin.plugins():
                for t in p.possible_media_types:
                    if not t in possible:
                        possible.append(t)
            try:
                type = possible[(possible.index(self.media_type)+1) % len(possible)]
            except (IndexError, ValueError), e:
                return super(Directory, self).eventhandler(event)
            self.media_type = self.menu_type = type
            # deactivate autoplay but not save it
            self.item_menu.autoselect = False
            self.browse()
            freevo.OSD_MESSAGE.post('%s view' % type)
            return True
        if event == freevo.DIRECTORY_TOGGLE_HIDE_PLAYED:
            self.hide_played = not self.config2value('hide_played')
            self.item_menu.autoselect = False
            self.browse()
            if self.hide_played:
                freevo.OSD_MESSAGE.post('Hide played items')
            else:
                freevo.OSD_MESSAGE.post('Show all items')
        return super(Directory, self).eventhandler(event)

    def _set_configure_var(self, var, name, choices):
        """
        Update the variable update the menu.
        """
        stored = getattr(self, var.lower())
        for pos, (value, txt) in enumerate(choices):
            if value == stored:
                break
        else:
            pos = 0
        current = choices[(pos + 1) % len(choices)]
        setattr(self, var, current[0])
        # change name
        item = self.menustack.current.selected
        item.name = name + ': '  + current[1]
        # FIXME: rebuild menu
        self.menustack.refresh(True)
        self.menustack.current.state += 1
        self.menustack.context.sync(force=True)

    @property
    def cfgitems(self):
        """
        Show the configure dialog for the item.
        """
        items = []
        for i, name, values, descr in [
            ('sort_method', _('Sort method'),
             (('auto', _('auto')), ('name', _('name')), ('smart', _('smart')),
              ('filename', _('filename')), ('date', _('date'))),
             _('How to sort items.')),
            ('autoplay_single_item', _('Autoplay single item'),
             ((None, _('auto')), (True, _('on')), (False, _('off' ))),
             _('Don\'t show directory if only one item exists and auto select it.')),
            ('autoplay_items', _('Autoplay items'),
             ((None, _('auto')), (True, _('on')), (False, _('off' ))),
             _('Autoplay the whole directory as playlist when it contains only files.')),
            ('isplaylist', _('Is playlist'),
             ((None, _('auto')), (True, _('on')), (False, _('off' ))),
             _('Handle the directory as playlist and play the next item when one is done.')) ,
            ('hide_played', _('Hide played items'),
             ((None, _('auto')), (True, _('on')), (False, _('off' ))),
             _('Hide items already played.'))]:
            stored = getattr(self, i.lower())
            for value, txt in values:
                if value == stored:
                    break
            else:
                value, txt = values[0]
            action = freevo.ActionItem(name + ': '  + txt, self, self._set_configure_var, descr)
            action.parameter(var=i, name=name, choices=list(values))
            items.append(action)
        return items

    def config2value(self, attr):
        value = getattr(self, attr)
        if value not in (None, 'auto'):
            return value
        if isinstance(self.parent, Directory):
            # return the value from the parent (auto)
            return self.parent.config2value(attr)
        # auto and no parent, use config file values
        if attr == 'sort_method':
            if self.menu_type == 'tv':
                return config.tvsort
            return config.sort
        value = getattr(config, attr, False)
        if isinstance(value, bool):
            return value
        return self.media_type in value.split(',')
