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

# freevo imports
import config
import util
import mediadb
from mediadb.globals import *

import menu
import plugin
import fxditem

from menu import Item, Files, Action, ActionItem
from playlist import Playlist
from event import *

import gui
import gui.theme
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

                 ('DIRECTORY_FORCE_SKIN_LAYOUT', _('Force Skin Layout'),
                  _('Force skin to a specific layout. This option doesn\'t ' \
                    'work with all skins and the result may differ based on ' \
                    'the skin.'), False),

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
        self.needs_update = False

        if isinstance(directory, mediadb.ItemInfo):
            self.info = directory
            directory = directory.filename
        else:
            directory = os.path.abspath(directory)
            self.info = mediadb.get(directory)

        # create full path
        directory = os.path.normpath(directory)
        # remove softlinks from path
        directory = os.path.realpath(directory) + '/'

        # get cover from cache
        image = self.info[COVER]
        if image:
            self.image = image
        
        # store Files information for moving/copying
        self.files = Files()
        if self.media:
            self.files.read_only = True
        self.files.append(directory)

        self.dir = directory
        self.url = directory
        
        if name:
            self.name = Unicode(name)
        else:
            self.name = self.info[FILETITLE]

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

        self.folder_fxd = self.info['fxd']
        if self.folder_fxd:
            self.set_fxd_file(self.folder_fxd)
        else:
            self.folder_fxd = directory+'/folder.fxd'

        # Check mimetype plugins if they want to add something
        for p in plugin.mimetype(display_type):
            p.dirinfo(self)

        if self.DIRECTORY_SORT_BY_DATE == 2 and self.display_type != 'tv':
            self.DIRECTORY_SORT_BY_DATE = 0


    def set_fxd_file(self, file):
        """
        Set self.folder_fxd and parse it
        """
        self.folder_fxd = file
        if self.folder_fxd and os.path.isfile(self.folder_fxd):
            if self.display_type == 'tv':
                display_type = 'video'
            try:
                parser = util.fxdparser.FXD(self.folder_fxd)
                parser.set_handler('folder', self.read_folder_fxd)
                parser.set_handler('skin', self.read_folder_fxd)
                parser.parse()
            except:
                log.exception("fxd file %s corrupt" % self.folder_fxd)


    def read_folder_fxd(self, fxd, node):
        '''
        parse the xml file for directory settings

	<?xml version="1.0" ?>
	<freevo>
	  <folder title="Incoming TV Shows" cover-img="foo.jpg">
	    <setvar name="directory_autoplay_single_item" val="0"/>
	    <info>
	      <content>Episodes for current tv shows not seen yet</content>
	    </info>
	  </folder>
	</freevo>
        '''
        if node.name == 'skin':
            self.skin_fxd = self.folder_fxd
            return

        # read attributes
        self.name = Unicode(fxd.getattr(node, 'title', self.name))

        image = fxd.childcontent(node, 'cover-img')
        if image and vfs.isfile(os.path.join(self.dir, image)):
            self.image = os.path.join(self.dir, image)

        # parse <info> tag
        fxd.parse_info(fxd.get_children(node, 'info', 1), self,
                       {'description': 'content', 'content': 'content' })

        for child in fxd.get_children(node, 'setvar', 1):
            # <setvar name="directory_smart_sort" val="1"/>
            for v,n,d, type_list in self.all_variables:
                if child.attrs[('', 'name')].upper() == v.upper():
                    if type_list:
                        if int(child.attrs[('', 'val')]):
                            setattr(self, v, [self.display_type])
                        else:
                            setattr(self, v, [])
                    else:
                        try:
                            setattr(self, v, int(child.attrs[('', 'val')]))
                        except ValueError:
                            setattr(self, v, child.attrs[('', 'val')])
                    self.modified_vars.append(v)


    def __is_type_list_var(self, var):
        """
        return if this variable to be saved is a type_list
        """
        for v,n,d, type_list in self.all_variables:
            if v == var:
                return type_list
        return False


    def write_folder_fxd(self, fxd, node):
        """
        callback to save the modified fxd file
        """
        # remove old setvar
        for child in copy.copy(node.children):
            if child.name == 'setvar':
                node.children.remove(child)

        # add current vars as setvar
        for v in self.modified_vars:
            if self.__is_type_list_var(v):
                if getattr(self, v):
                    val = 1
                else:
                    val = 0
            else:
                val = getattr(self, v)
            fxd.add(fxd.XMLnode('setvar', (('name', v.lower()),
                                           ('val', val))), node, 0)


    def __getitem__(self, key):
        """
        return the specific attribute
        """
        if key == 'type':
            if self.media:
                return _('Directory on disc [%s]') % self.media.label
            return _('Directory')

        if key == 'num_items':
            display_type = self.display_type or 'all'
            if self.display_type == 'tv':
                display_type = 'video'
            return self['num_%s_items' % display_type] + self['num_dir_items']

        if key == 'num_play_items':
            display_type = self.display_type
            if self.display_type == 'tv':
                display_type = 'video'
            return self['num_%s_items' % display_type]

        if key in ( 'freespace', 'totalspace' ):
            if self.media:
                return None

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
        if event == DIRECTORY_CHANGE_DISPLAY_TYPE and self.item_menu.visible:
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
    # metainfo
    # ======================================================================

    def __init_info__(self):
        """
        create some metainfo for the directory
        """
        if not Playlist.__init_info__(self):
            # nothing new
            return False
        
        display_type = self.display_type

        if self.display_type == 'tv':
            display_type = 'video'

        name = display_type or 'all'

        if self.info['num_%s_items' % name] != None:
            # info is already stored, no new data
            return False
        
        log.info('create metainfo for %s', self.dir)
        if self.media:
            umount = not self.media.is_mounted()
            self.media.mount()

        # get listing
        listing = mediadb.Listing(self.dir)
        if listing.num_changes:
            listing.update(fast=True)

        # play items and playlists
        num_play_items = 0
        for p in plugin.mimetype(display_type):
            num_play_items += p.count(self, listing)

        # normal DirItems
        num_dir_items = len(listing.get_dir())

        # store info
        self.info.store_with_mtime('num_%s_items' % name, num_play_items)
        self.info.store_with_mtime('num_dir_items', num_dir_items)

        if self.media and umount:
            self.media.umount()

        return True
    

    # ======================================================================
    # actions
    # ======================================================================

    def actions(self):
        """
        return a list of actions for this item
        """
        if self.media:
            # mount media if not mounted
            umount = not self.media.is_mounted()
            self.media.mount()

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

        # FIXME: add this function again
        # if self.folder_fxd:
        #   items += fxditem.mimetype.get(self, [self.folder_fxd])

        if self.media and umount:
            self.media.umount()

        return items



    def play(self, random=False, recursive=False):
        """
        play directory
        """
        # FIXME: add password checking here
        if self.media and not self.media.is_mounted():
            self.media.mount()
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
        

    def check_password_then_browse(self):
        """
        password checker
        """
        # are we on a ROM_DRIVE and have to mount it first?
        for media in vfs.mountpoints:
            if self.dir.startswith(media.mountdir):
                media.mount()
                self.media = media

        if vfs.isfile(self.dir + '/.password'):
            log.warning('password protected dir')
            pb = InputBox(text=_('Enter Password'), handler=self.browse_pass_cb,
                          type='password')
            pb.show()
        else:
            self.browse(authstatus=1)


    def browse_pass_cb(self, word=None):
        """
        read the contents of self.dir/.passwd and compare to word
        callback for check_password_then_browse
        """
        try:
            pwfile = vfs.open(self.dir + '/.password')
            line = pwfile.readline()
        except IOError, e:
            log.error('error %d (%s) reading password file for %s' % \
                        (e.errno, e.strerror, self.dir))
            return

        pwfile.close()
        password = line.strip()
        if word == password:
            self.browse(authstatus=1)
        else:
            MessageBox(_('Password incorrect')).show()
            self.browse(authstatus=-1)


    def browse(self, update=False, authstatus=0):
        """
        build the items for the directory
        """
        # check for password
        if 0:
            # This code breaks the menu. In some cases a directory
            # menu is twice or even more often in the stack.
            # So it is disabled until fixed!
            if authstatus == 0:
                self.check_password_then_browse()
            elif authstatus == -1:
                log.info('authorization failed for browsing %s' % self.dir)
                return
	    

        if update and not (self.listing and self.item_menu.visible):
            # not visible right now, do not update
            self.needs_update = True
            return
        t0 = time.time()
        self.playlist   = []
        play_items = []
        dir_items  = []
        pl_items   = []

        if self.media and not self.media.is_mounted():
            self.media.mount()

        if update:
            # Delete possible skin settings
            # FIXME: This is a very bad handling, maybe signals?
            if hasattr(self.item_menu, 'skin_default_has_description'):
                del self.item_menu.skin_default_has_description
            if hasattr(self.item_menu, 'skin_default_no_images'):
                del self.item_menu.skin_default_no_images
            if hasattr(self.item_menu, 'skin_force_text_view'):
                del self.item_menu.skin_force_text_view
            # maybe the cover changed
            self.image = self.info['image']

        elif not os.path.exists(self.dir):
            # FIXME: better handling!!!!!
	    MessageBox(_('Directory does not exist')).show()
            return

        self.needs_update = False
        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        t1 = time.time()
        listing = mediadb.Listing(self.dir)
        t2 = time.time()

        if listing.num_changes > 5:
            if self.media:
                text = _('Scanning disc, be patient...')
            else:
                text = _('Scanning directory, be patient...')
            listing.update(fast=True)
        elif listing.num_changes:
            listing.update()
        t3 = time.time()
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

        t4 = time.time()
        # normal DirItems
        for item in listing.get_dir():
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

        t5 = time.time()

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

        t6 = time.time()

        if self['num_dir_items'] != len(dir_items):
            self['num_dir_items'] = len(dir_items)

        if self.info['num_%s_items' % display_type] != \
               len(play_items) + len(pl_items):
            self.info['num_%s_items' % display_type] = len(play_items) + \
                                                       len(pl_items)

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
            # update because of dirwatcher changes
            self.item_menu.set_items(items)

        else:
            # normal menu build
            item_menu = menu.Menu(self.name, items, reload_func=self.reload,
                                  item_types = display_type,
                                  force_skin_layout = \
                                  self.DIRECTORY_FORCE_SKIN_LAYOUT)

            if self.skin_fxd:
                item_menu.theme = self.skin_fxd
            item_menu.autoselect = self.DIRECTORY_AUTOPLAY_SINGLE_ITEM
            self.pushmenu(item_menu)

            self.item_menu = kaa.weakref(item_menu)
            callback = kaa.notifier.Callback(self.browse, True)
            mediadb.watcher.cwd(listing, callback)

        t7 = time.time()
        # print t2 - t1, t4 - t3, t5 - t4, t6 - t5, t7 - t6, t7 - t0



    def reload(self):
        """
        called when we return to this menu
        """
        callback = kaa.notifier.Callback(self.browse, True)
        if mediadb.watcher.cwd(self.listing, callback):
            # some files changed
            self.needs_update = True
        if self.needs_update:
            # update directory
            log.info('directory needs update')
            callback()
        # we (may) changed the menu, don't build a new one
        return None


    # ======================================================================
    # configure submenu
    # ======================================================================


    def configure_set_name(self, name):
        """
        return name for the configure menu
        """
        if name in self.modified_vars:
            if name == 'FORCE_SKIN_LAYOUT':
                return 'ICON_RIGHT_%s_%s' % (str(getattr(self, name)),
                                             str(getattr(self, name)))
            elif getattr(self, name):
                return 'ICON_RIGHT_ON_' + _('on')
            else:
                return 'ICON_RIGHT_OFF_' + _('off')
        else:
            if name == 'FORCE_SKIN_LAYOUT':
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

        # for DIRECTORY_FORCE_SKIN_LAYOUT max = number of styles in the menu
        if var == 'FORCE_SKIN_LAYOUT':
            if self.display_type and \
                   gui.theme.get().menu.has_key(self.display_type):
                area = gui.theme.get().menu[self.display_type]
            else:
                area = gui.theme.get().menu['default']
            max = len(area.style) - 1

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

        try:
            parser = util.fxdparser.FXD(self.folder_fxd)
            parser.set_handler('folder', self.write_folder_fxd, 'w', True)
            parser.save()
        except:
            log.exception("fxd file %s corrupt" % self.folder_fxd)

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
        show the configure dialog for folder specific settings in folder.fxd
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
