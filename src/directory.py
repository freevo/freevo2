# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# directory.py - Directory handling
# -----------------------------------------------------------------------------
# $Id$
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

# python imports
import os
import stat
import copy
import logging
import time

import notifier

# freevo imports
import config
import util
import mediadb
from mediadb.globals import *

import menu
import plugin
import fxditem
import eventhandler

from item import Item, FileInformation
from playlist import Playlist
from event import *

import gui
from gui import InputBox, AlertBox, ProgressBox

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



class DirItem(Playlist):
    """
    class for handling directories
    """
    def __init__(self, directory, parent, name = '', display_type = None,
                 add_args = None):
        Playlist.__init__(self, parent=parent, display_type=display_type)
        self.type = 'dir'
        self.menu  = None
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
        
        # store FileInformation for moving/copying
        self.files = FileInformation()
        if self.media:
            self.files.read_only = True
        self.files.append(directory)

        self.dir = directory
        
        if name:
            self.name = Unicode(name)
        else:
            self.name = self.info[FILETITLE]

        if add_args == None and hasattr(parent, 'add_args'):
            add_args = parent.add_args
        self.add_args = add_args

        if self.parent and hasattr(parent, 'skin_display_type'):
            self.skin_display_type = parent.skin_display_type
        elif parent:
            self.skin_display_type = parent.display_type
        else:
            self.skin_display_type = display_type

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

        return Item.__getitem__(self, key)


    # eventhandler for this item
    def eventhandler(self, event, menuw=None):
        if event == DIRECTORY_CHANGE_DISPLAY_TYPE and \
               menuw.menustack[-1] == self.menu:
            possible_display_types = [ ]

            for p in plugin.get('mimetype'):
                for t in p.display_type:
                    if not t in possible_display_types:
                        possible_display_types.append(t)

            try:
                pos = possible_display_types.index(self.display_type)
                type = possible_display_types[(pos+1) % \
                                              len(possible_display_types)]

                menuw.delete_menu(allow_reload = False)

                newdir = DirItem(self.dir, self.parent, self.name, type,
                                 self.add_args)
                newdir.DIRECTORY_AUTOPLAY_SINGLE_ITEM = False
                newdir.cwd(menuw=menuw)

                menuw.menustack[-2].selected = newdir
                pos = menuw.menustack[-2].choices.index(self)
                menuw.menustack[-2].choices[pos] = newdir
                eventhandler.post(Event(OSD_MESSAGE, arg='%s view' % type))
                return True
            except (IndexError, ValueError):
                pass

        return Playlist.eventhandler(self, event, menuw)


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
        need_umount = False
        if self.media:
            need_umount = not self.media.is_mounted()
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

        if need_umount:
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
            self.media.mount()

        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        items = [ ( self.cwd, _('Browse directory')) ]

        if self.info['num_%s_items' % display_type]:
            items.append((self.play, _('Play all files in directory')))

        if display_type in self.DIRECTORY_AUTOPLAY_ITEMS and \
               not self['num_dir_items']:
            items.reverse()

        if self.info['num_%s_items' % display_type]:
            items.append((self.play_random, _('Random play all items')))
        if self['num_dir_items']:
            items += [ (self.play_random_recursive,
                        _('Recursive random play all items')),
                       (self.play_recursive, _('Recursive play all items')) ]

        items.append((self.configure, _('Configure directory'), 'configure'))

        # FIXME: add this function again
        # if self.folder_fxd:
        #   items += fxditem.mimetype.get(self, [self.folder_fxd])

        if self.media:
            self.media.umount()

        return items



    def cwd(self, arg=None, menuw=None):
        """
        browse directory
        """
        self.check_password_and_build(arg=None, menuw=menuw)


    def play(self, arg=None, menuw=None):
        """
        play directory
        """
        if arg == 'next':
            Playlist.play(self, arg=arg, menuw=menuw)
        else:
            self.check_password_and_build(arg='play', menuw=menuw)


    def play_random(self, arg=None, menuw=None):
        """
        play in random order
        """
        self.check_password_and_build(arg='playlist:random', menuw=menuw)


    def play_recursive(self, arg=None, menuw=None):
        """
        play recursive
        """
        self.check_password_and_build(arg='playlist:recursive', menuw=menuw)


    def play_random_recursive(self, arg=None, menuw=None):
        """
        play recursive in random order
        """
        self.check_password_and_build(arg='playlist:random_recursive',
                                      menuw=menuw)


    def check_password_and_build(self, arg=None, menuw=None):
        """
        password checker
        """
        if not self.menuw:
            self.menuw = menuw

        # are we on a ROM_DRIVE and have to mount it first?
        for media in vfs.mountpoints:
            if self.dir.startswith(media.mountdir):
                media.mount()
                self.media = media

        # FIXME: add support again when InputBox is working
	if vfs.isfile(self.dir + '/.password') and 0:
	    log.warning('password protected dir')
            self.arg   = arg
            self.menuw = menuw
	    pb = InputBox(text=_('Enter Password'), handler=self.pass_cmp_cb,
                          type='password')
	    pb.show()
	else:
	    self.build(arg=arg, menuw=menuw)


    def pass_cmp_cb(self, word=None):
        """
        read the contents of self.dir/.passwd and compare to word
        callback for check_password_and_build
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
	    self.build(self.arg, self.menuw)
	else:
	    pb = AlertBox(text=_('Password incorrect'))
	    pb.show()
            return


    def build(self, arg=None, menuw=None):
        """
        build the items for the directory
        """
        if arg == 'update' and not (self.listing and self.menuw and \
                                    self.menuw.menustack[-1] == self.menu and \
                                    eventhandler.is_menu()):
            # not visible right now, do not update
            self.needs_update = True
            return

        t0 = time.time()
        self.playlist   = []
        self.play_items = []
        self.dir_items  = []
        self.pl_items   = []

        if self.media:
            self.media.mount()

        if arg == 'update':
            if not self.menu.choices:
                selected_pos = -1
            else:
                # store the current selected item
                selected_id  = self.menu.selected.__id__()
                selected_pos = self.menu.choices.index(self.menu.selected)
            # warning: self.menu is a weakref!
            self.menu.delattr('skin_default_has_description')
            self.menu.delattr('skin_default_no_images')
            self.menu.delattr('skin_force_text_view')

        elif not os.path.exists(self.dir):
            # FIXME: better handling!!!!!
	    AlertBox(text=_('Directory does not exist')).show()
            return

        self.needs_update = False
        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        if arg and arg.startswith('playlist:'):
            if arg.endswith(':random'):
                pl = Playlist(playlist = [ (self.dir, 0) ], parent = self,
                              display_type=display_type, random=True)
            elif arg.endswith(':recursive'):
                pl = Playlist(playlist = [ (self.dir, 1) ], parent = self,
                              display_type=display_type, random=False)
            elif arg.endswith(':random_recursive'):
                pl = Playlist(playlist = [ (self.dir, 1) ], parent = self,
                              display_type=display_type, random=True)
            else:
                return
            pl.play(menuw=menuw)
            return

        t1 = time.time()
        listing = mediadb.Listing(self.dir)
        t2 = time.time()

        if listing.num_changes > 5:
            if self.media:
                text = _('Scanning disc, be patient...')
            else:
                text = _('Scanning directory, be patient...')
            #popup = ProgressBox(text, full=listing.num_changes)
            #popup.show()
            #listing.update(popup.tick)
            #popup.destroy()
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
                    self.pl_items.append(i)
                elif i.type == 'dir':
                    self.dir_items.append(i)
                else:
                    self.play_items.append(i)

        t4 = time.time()
        # normal DirItems
        for item in listing.get_dir():
            d = DirItem(item, self, display_type = self.display_type)
            self.dir_items.append(d)

        # remember listing
        self.listing = listing

        # remove same beginning from all play_items
        substr = ''
        if len(self.play_items) > 4 and len(self.play_items[0].name) > 5:
            substr = self.play_items[0].name[:-5].lower()
            for i in self.play_items[1:]:
                if len(i.name) > 5:
                    substr = util.find_start_string(i.name.lower(), substr)
                    if not substr or len(substr) < 10:
                        break
                else:
                    break
            else:
                for i in self.play_items:
                    i.name = util.remove_start_string(i.name, substr)

        t5 = time.time()

        #
        # sort all items
        #

        # sort directories
        if self.DIRECTORY_SMART_SORT:
            self.dir_items.sort(lambda l, o: util.smartsort(l.dir,o.dir))
        else:
            self.dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))

        # sort playlist
        self.pl_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))

        # sort normal items
        if self.DIRECTORY_SORT_BY_DATE:
            self.play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                                  o.sort('date').upper()))
        elif self['%s_advanced_sort' % display_type]:
            self.play_items.sort(lambda l, o: cmp(l.sort('advanced').upper(),
                                                  o.sort('advanced').upper()))
        else:
            self.play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                                  o.sort().upper()))

        t6 = time.time()

        if self['num_dir_items'] != len(self.dir_items):
            self['num_dir_items'] = len(self.dir_items)

        if self.info['num_%s_items' % display_type] != \
               len(self.play_items) + len(self.pl_items):
            self.info['num_%s_items' % display_type] = len(self.play_items) + \
                                                       len(self.pl_items)

        if self.DIRECTORY_REVERSE_SORT:
            self.dir_items.reverse()
            self.play_items.reverse()
            self.pl_items.reverse()

        # delete pl_items if they should not be displayed
        if self.display_type and not self.display_type in \
               self.DIRECTORY_ADD_PLAYLIST_FILES:
            self.pl_items = []

        # add all playable items to the playlist of the directory
        # to play one files after the other
        if not self.display_type or self.display_type in \
               self.DIRECTORY_CREATE_PLAYLIST:
            self.playlist = self.play_items


        # build a list of all items
        items = self.dir_items + self.pl_items + self.play_items

        # random playlist (only active for audio)
        if self.display_type and self.display_type in \
               self.DIRECTORY_ADD_RANDOM_PLAYLIST \
               and len(self.play_items) > 1:
            pl = Playlist(_('Random playlist'), self.play_items, self,
                          random=True)
            pl.autoplay = True
            items = [ pl ] + items


        #
        # action
        #

        if arg == 'update':
            # update because of dirwatcher changes
            self.menu.choices = items

            if selected_pos != -1:
                # we had a selection before, try to find it again
                for i in items:
                    if Unicode(i.__id__()) == Unicode(selected_id):
                        self.menu.set_selection(i)
                        break
                else:
                    # item is gone now, try to the selection close
                    # to the old item
                    pos = max(0, min(selected_pos-1, len(items)-1))
                    if items:
                        self.menu.set_selection(items[pos])
                    else:
                        self.menu.set_selection(None)
            else:
                # nothing was selected, select first item if possible
                if len(items):
                    self.menu.set_selection(items[0])
                else:
                    self.menu.set_selection(None)
            self.menuw.refresh()


        elif len(items) == 1 and items[0].actions() and \
                 self.DIRECTORY_AUTOPLAY_SINGLE_ITEM:
            # autoplay
	    action = items[0].actions()[0]
	    if isinstance( action, tuple ):
	    	action[ 0 ](menuw=menuw)
	    else:
	    	action(menuw=menuw)

        elif arg=='play' and self.play_items:
            # called by play function
            self.playlist = self.play_items
            Playlist.play(self, menuw=menuw)

        else:
            # normal menu build
            item_menu = menu.Menu(self.name, items, reload_func=self.reload,
                                  item_types = self.skin_display_type,
                                  force_skin_layout = \
                                  self.DIRECTORY_FORCE_SKIN_LAYOUT)

            if self.skin_fxd:
                item_menu.theme = self.skin_fxd

            menuw.pushmenu(item_menu)

            self.menu = util.weakref(item_menu)

            callback = notifier.Callback(self.build, 'update', self.menuw)
            mediadb.watcher.cwd(listing, callback)
            self.menuw = menuw

        t7 = time.time()
        # print t2 - t1, t4 - t3, t5 - t4, t6 - t5, t7 - t6, t7 - t0



    def reload(self):
        """
        called when we return to this menu
        """
        callback = notifier.Callback(self.build, 'update', self.menuw)
        mediadb.watcher.cwd(self.listing, callback)
        if self.needs_update:
            log.info('directory needs update')
            callback()
        else:
            mediadb.watcher.check()
        # we changed the menu, don't build a new one
        return None


    def delete(self):
        """
        delete function for this item
        """
        Playlist.delete(self)
        self.play_items = []
        self.dir_items  = []
        self.pl_items   = []


    def __del__(self):
        """
        delete function of memory debugging
        """
        _mem_debug_('dir ', self.name, 2)


    # ======================================================================
    # configure submenu
    # ======================================================================


    def configure_set_name(self, name):
        """
        return name for the configure menu
        """
        if name in self.modified_vars:
            if name == 'FORCE_SKIN_LAYOUT':
                return 'ICON_RIGHT_%s_%s' % (str(getattr(self, arg)),
                                             str(getattr(self, arg)))
            elif getattr(self, name):
                return 'ICON_RIGHT_ON_' + _('on')
            else:
                return 'ICON_RIGHT_OFF_' + _('off')
        else:
            if name == 'FORCE_SKIN_LAYOUT':
                return 'ICON_RIGHT_OFF_' + _('off')
            else:
                return 'ICON_RIGHT_AUTO_' + _('auto')


    def configure_set_var(self, arg=None, menuw=None):
        """
        Update the variable in arg and change the menu. This function is used
        by 'configure'
        """

        # get current value, None == no special settings
        if arg in self.modified_vars:
            if self.__is_type_list_var(arg):
                if getattr(self, arg):
                    current = 1
                else:
                    current = 0
            else:
                current = getattr(self, arg)
        else:
            current = None

        # get the max value for toggle
        max = 1

        # for DIRECTORY_FORCE_SKIN_LAYOUT max = number of styles in the menu
        if arg == 'FORCE_SKIN_LAYOUT':
            if self.display_type and \
                   gui.get_theme().menu.has_key(self.display_type):
                area = gui.get_theme().menu[self.display_type]
            else:
                area = gui.get_theme().menu['default']
            max = len(area.style) - 1

        # switch from no settings to 0
        if current == None:
            self.modified_vars.append(arg)
            if self.__is_type_list_var(arg):
                setattr(self, arg, [])
            else:
                setattr(self, arg, 0)

        # inc variable
        elif current < max:
            if self.__is_type_list_var(arg):
                setattr(self, arg, [self.display_type])
            else:
                setattr(self, arg, current+1)

        # back to no special settings
        elif current == max:
            if self.parent and hasattr(self.parent, arg):
                setattr(self, arg, getattr(self.parent, arg))
            if hasattr(config, arg):
                setattr(self, arg, getattr(config, arg))
            else:
                setattr(self, arg, False)
            self.modified_vars.remove(arg)

        # create new item with updated name
        item = copy.copy(menuw.menustack[-1].selected)
        item.name = item.name[:item.name.find(u'\t') + 1] + \
                    self.configure_set_name(arg)

        try:
            parser = util.fxdparser.FXD(self.folder_fxd)
            parser.set_handler('folder', self.write_folder_fxd, 'w', True)
            parser.save()
        except:
            log.exception("fxd file %s corrupt" % self.folder_fxd)

        # rebuild menu
        menuw.menustack[-1].choices[menuw.menustack[-1].choices.\
                                    index(menuw.menustack[-1].selected)] = item
        menuw.menustack[-1].selected = item
        menuw.refresh(reload=1)


    def configure_set_display_type(self, arg=None, menuw=None):
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

        # create new item with updated name
        item = copy.copy(menuw.menustack[-1].selected)
        item.name = item.name[:item.name.find(u'\t')]  + name

        # rebuild menu
        menuw.menustack[-1].choices[menuw.menustack[-1].choices.\
                                    index(menuw.menustack[-1].selected)] = item
        menuw.menustack[-1].selected = item
        menuw.refresh(reload=1)


    def configure(self, arg=None, menuw=None):
        """
        show the configure dialog for folder specific settings in folder.fxd
        """
        items = []
        for i, name, descr, type_list in self.all_variables:
            if name == '':
                continue
            name += '\t'  + self.configure_set_name(i)
            mi = menu.MenuItem(name, self.configure_set_var, i)
            mi.description = descr
            items.append(mi)

        if self.parent and self.parent.display_type:
            if self.display_type:
                name = u'\tICON_RIGHT_OFF_' + _('off')
            else:
                name = u'\tICON_RIGHT_ON_' + _('on')

            mi = menu.MenuItem(_('Show all kinds of items') + name,
                               self.configure_set_display_type)
            descr = _('Show video, audio and image items in this directory')
            mi.description = descr
            items.append(mi)

        m = menu.Menu(_('Configure'), items)
        m.table = (80, 20)
        m.back_one_menu = 2
        menuw.pushmenu(m)
