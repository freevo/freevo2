# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# item.py - Template for an item
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains a basic item for the menu and a special one for items
# based on media content. There is also a base class for actions to be
# returned by the actions() function.
#
# First edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
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

__all__ = [ 'FileInformation', 'Action', 'Item', 'MediaItem' ]


# python imports
import os
import gettext
import shutil
import logging

# freevo imports
import plugin
import util

from sysconfig import Unicode
from util import vfs
import util.mediainfo as mediainfo

# get logging object
log = logging.getLogger()


class FileInformation:
    """
    File operations for an item.
    """
    def __init__(self):
        self.files     = []
        self.fxd_file  = ''
        self.image     = ''
        self.read_only = False


    def append(self, filename):
        """
        Append a file to the list.
        """
        self.files.append(filename)


    def get(self):
        """
        Return all files.
        """
        return self.files


    def copy_possible(self):
        """
        Return true if it is possible to copy the files.
        """
        return self.files != []


    def copy(self, destdir):
        """
        Copy all files to destdir.
        """
        for f in self.files + [ self.fxd_file, self.image ]:
            if f:
                if vfs.isoverlay(f):
                    d = vfs.getoverlay(destdir)
                else:
                    d = destdir
                if not os.path.isdir(d):
                    os.makedirs(d)
                shutil.copy(f, d)


    def move_possible(self):
        """
        Return true if it is possible to move the files.
        """
        return self.files and not self.read_only


    def move(self, destdir):
        """
        Move all files to destdir.
        """
        for f in self.files + [ self.fxd_file, self.image ]:
            if f:
                if vfs.isoverlay(f):
                    d = vfs.getoverlay(destdir)
                else:
                    d = destdir
                if not os.path.isdir(d):
                    os.makedirs(d)
                os.system('mv "%s" "%s"' % (f, d))


    def delete_possible(self):
        """
        Return true if it is possible to delete the files.
        """
        return self.files and not self.read_only


    def delete(self):
        """
        Delete all files.
        """
        for f in self.files + [ self.fxd_file, self.image ]:
            if not f:
                continue
            if os.path.isdir(f) and not os.path.islink(f):
                shutil.rmtree(f, ignore_errors=1)
            else:
                try:
                    os.unlink(f)
                except:
                    log.error('can\'t delete %s' % f)


class Action:
    """
    Action for item.actions()
    """
    def __init__(self, name, function=None, arg=None, shortcut=None,
                 description=None):
        self.name = name
        self.function = function
        self.arg = arg
        self.shortcut = shortcut
        self.description = description


    def __call__(self, menuw=None):
        """
        call the function
        """
        if self.function:
            self.function(arg=self.arg, menuw=menuw)


class Item:
    """
    Item class. This is the base class for all items in the menu.
    It's a template for MenuItem and for other info items like
    VideoItem, AudioItem and ImageItem
    """
    def __init__(self, parent=None, info=None):
        """
        Init the item. Sets all needed variables, if parent is given also
        inherit some settings from there. Set self.info to info if given.
        """
        if not hasattr(self, 'type'):
            self.type     = None            # e.g. video, audio, dir, playlist

        self.name         = u''             # name in menu
        self.parent       = parent          # parent item
        self.icon         = None
        if info and isinstance(info, mediainfo.Info):
            self.info     = copy.copy(info)
        else:
            self.info     = mediainfo.Info(None, None, info)
        self.menuw        = None
        self.description  = ''

        self.eventhandler_plugins = []

        if not hasattr(self, 'autovars'):
            self.autovars = []

        if parent:
            if info and hasattr(parent, 'DIRECTORY_USE_MEDIAID_TAG_NAMES') \
                   and parent.DIRECTORY_USE_MEDIAID_TAG_NAMES and \
                   self.info.has_key('title'):
                self.name = self.info['title']

            self.image = parent.image
            if hasattr(parent, 'is_mainmenu_item'):
                self.image = None
            self.skin_fxd    = parent.skin_fxd
            self.media       = parent.media
        else:
            self.image        = None            # imagefile
            self.skin_fxd     = None            # skin informationes etc.
            self.media        = None

        self.fxd_file = None



    def __setitem__(self, key, value):
        """
        set the value of 'key' to 'val'
        """
        for var, val in self.autovars:
            if key == var:
                if val == value:
                    if not self.delete_info(key):
                        log.warning( u'unable to store info for \'%s\'' % \
                                     self.name )
                else:
                    self.store_info(key, value)
                return
        self.info[key] = value


    def store_info(self, key, value):
        """
        store the key/value in metadata
        """
        if isinstance(self.info, mediainfo.Info):
            if not self.info.store(key, value):
                log.warning( u'unable to store info for \'%s\'' % self.name)
        else:
            log.warning( u'unable to store info for item \'%s\'' % self.name)


    def delete_info(self, key):
        """
        delete entry for metadata
        """
        if isinstance(self.info, mediainfo.Info):
            return self.info.delete(key)
        else:
            log.warning('unable to delete info for that kind of item')


    def __id__(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        if hasattr(self, 'url'):
            return self.url
        return self.name


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        return u'0%s' % self.name


    def actions(self):
        """
        returns a list of possible actions on this item. The first
        one is autoselected by pressing SELECT
        """
        return None


    def __call__(self, arg=None, menuw=None):
        """
        call first action in the actions() list
        """
        if self.actions():
            return self.actions()[0][0](arg=arg, menuw=menuw)


    def eventhandler(self, event, menuw=None):
        """
        simple eventhandler for an item
        """

        if not menuw:
            menuw = self.menuw

        for p in self.eventhandler_plugins:
            if p(event, self, menuw):
                return True

        # give the event to the next eventhandler in the list
        if self.parent:
            return self.parent.eventhandler(event, menuw)

        return False


    def plugin_eventhandler(self, event, menuw=None):
        """
        eventhandler for special pligins for this item
        """
        if not hasattr(self, '__plugin_eventhandler__'):
            self.__plugin_eventhandler__ = []
            for p in plugin.get('item') + plugin.get('item_%s' % self.type):
                if hasattr(p, 'eventhandler'):
                    self.__plugin_eventhandler__.append(p.eventhandler)
        for e in self.__plugin_eventhandler__:
            if e(self, event, menuw):
                return True
        return False


    def __getitem__(self, attr):
        """
        return the specific attribute
        """
        if attr == 'length':
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


        if attr == 'length:min':
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
            return '%d min' % (length / 60)

        if attr[:7] == 'parent(' and attr[-1] == ')' and self.parent:
            return self.parent[attr[7:-1]]

        if attr[:4] == 'len(' and attr[-1] == ')':
            r = None
            if self.info.has_key(attr[4:-1]):
                r = self.info[attr[4:-1]]

            if (r == None or r == '') and hasattr(self, attr[4:-1]):
                r = getattr(self,attr[4:-1])
            if r != None:
                return len(r)
            return 0

        else:
            r = None
            if self.info.has_key(attr):
                r = self.info[attr]
            if (r == None or r == '') and hasattr(self, attr):
                r = getattr(self,attr)
            if r != None:
                return r
            if hasattr(self, 'autovars'):
                for var, val in self.autovars:
                    if var == attr:
                        return val
        return ''


    def delete(self):
        """
        callback when this item is deleted from the menu
        """
        self.parent = None


    def __del__(self):
        """
        delete function of memory debugging
        """
        _mem_debug_('item', self.name)




class MediaItem(Item):
    """
    This item is for a media. It's only a template for image, video
    or audio items
    """
    def __init__(self, type, parent):
        self.type = type
        Item.__init__(self, parent)


    def set_url(self, url, info=True, search_image=True):
        """
        Set a new url to the item and adjust all attributes depending
        on the url. Each MediaItem has to call this function. If info
        is True, search for additional information in mediainfo.
        """
        self.url = url                  # the url itself

        if not url:
            self.network_play = True    # network url, like http
            self.filename     = ''      # filename if it's a file:// url
            self.mode         = ''      # the type (file, http, dvd...)
            self.files        = None    # FileInformation
            self.mimetype     = ''      # extention or mode
            return

        if url.find('://') == -1:
            self.url = 'file://' + url

        self.files = FileInformation()
        if self.media:
            self.files.read_only = True

        self.mode = self.url[:self.url.find('://')]

        if self.mode == 'file':
            # The url is based on a file. We can search for images
            # and extra attributes here
            self.network_play = False
            self.filename     = self.url[7:]
            self.files.append(self.filename)
            if search_image:
                image = util.getimage(self.filename[:self.filename.rfind('.')])
                if image:
                    # there is an image with the same filename except
                    # the suffix is an image
                    self.image = image
                    self.files.image = image
                elif self.parent and self.parent.type != 'dir':
                    # search for cover.[png|jpg] the the current dir
                    cover = os.path.dirname(self.filename) + '/cover'
                    self.image = util.getimage(cover, self.image)
            # set the suffix of the file as mimetype
            self.mimetype = self.filename[self.filename.rfind('.')+1:].lower()
            if info:
                self.info = mediainfo.get(self.filename)
                try:
                    if self.parent.DIRECTORY_USE_MEDIAID_TAG_NAMES:
                        self.name = self.info['title'] or self.name
                except:
                    pass
                if not self.name:
                    self.name = self.info['title:filename']
            # Set a name for the item based on the filename
            if not self.name:
                self.name = util.getname(self.filename)

        else:
            # Mode is not file, it has to be a network url. Other
            # types like dvd are handled inside the derivated class
            self.network_play = True
            self.filename     = ''
            self.mimetype     = self.type
            if not self.name:
                self.name     = Unicode(self.url)


    def play(self, arg=None, menuw=None):
        """
        play the item
        """
        pass


    def stop(self, arg=None, menuw=None):
        """
        stop playing
        """
        pass
