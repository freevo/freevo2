# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# item.py - Template for an item
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.76  2004/08/05 17:38:25  dischi
# remove skin dep
#
# Revision 1.75  2004/08/01 10:56:00  dischi
# do not hide/show the menu, it can do that itself
#
# Revision 1.74  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.73  2004/05/29 12:33:16  dischi
# make it possible to access parent data
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


import os
import gettext
import shutil

import config
from event import *
import plugin
import util
import gui

from util import mediainfo, vfs, Unicode

class FileInformation:
    """
    file operations for an item
    """
    def __init__(self):
        self.files     = []
        self.fxd_file  = ''
        self.image     = ''
        self.read_only = False


    def append(self, filename):
        self.files.append(filename)


    def get(self):
        return self.files


    def copy_possible(self):
        return self.files != []

    
    def copy(self, destdir):
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
        return self.files and not self.read_only


    def move(self, destdir):
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
        return self.files and not self.read_only


    def delete(self):
        for f in self.files + [ self.fxd_file, self.image ]:
            if not f:
                continue
            if os.path.isdir(f) and not os.path.islink(f):
                shutil.rmtree(f, ignore_errors=1)
            else:
                try:
                    os.unlink(f)
                except:
                    print 'can\'t delete %s' % f
        
                

class Item:
    """
    Item class. This is the base class for all items in the menu. It's a template
    for MenuItem and for other info items like VideoItem, AudioItem and ImageItem
    """
    def __init__(self, parent=None, info=None, skin_type=None):
        """
        Init the item. Sets all needed variables, if parent is given also inherit
        some settings from there. Set self.info to info if given.
        """
        if not hasattr(self, 'type'):
            self.type     = None            # e.g. video, audio, dir, playlist

        self.name         = u''             # name in menu
        self.parent       = parent          # parent item to pass unmapped event
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

        if info and parent and hasattr(parent, 'DIRECTORY_USE_MEDIAID_TAG_NAMES') and \
               parent.DIRECTORY_USE_MEDIAID_TAG_NAMES and self.info.has_key('title'):
            self.name = self.info['title']
        
        if parent:
            self.image = parent.image
            if hasattr(parent, 'is_mainmenu_item'):
                self.image = None
            self.skin_fxd    = parent.skin_fxd
            self.media       = parent.media
            if hasattr(parent, '_'):
                self._ = parent._
        else:
            self.image        = None            # imagefile
            self.skin_fxd     = None            # skin informationes etc.
            self.media        = None

                
        self.fxd_file = None

        if skin_type:
            settings  = gui.get_settings()
            skin_info = settings.mainmenu.items
            imagedir  = settings.mainmenu.imagedir
            if skin_info.has_key(skin_type):
                skin_info  = skin_info[skin_type]
                self.name  = _(skin_info.name)
                self.image = skin_info.image
                if skin_info.icon:
                    self.icon = os.path.join(settings.icon_dir, skin_info.icon)
                if skin_info.outicon:
                    self.outicon = os.path.join(settings.icon_dir, skin_info.outicon)
            if not self.image and imagedir:
                self.image = util.getimage(os.path.join(imagedir, skin_type))
        

    def set_url(self, url, info=True, search_image=True):
        """
        Set a new url to the item and adjust all attributes depending
        on the url.
        """
        self.url              = url     # the url itself

        if not url:
            self.network_play = True    # network url, like http
            self.filename     = ''      # filename if it's a file:// url
            self.mode         = ''      # the type of the url (file, http, dvd...)
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
            self.network_play = False
            self.filename     = self.url[7:]
            self.files.append(self.filename)
            if search_image:
                image = util.getimage(self.filename[:self.filename.rfind('.')])
                if image:
                    self.image = image
                    self.files.image = image
                elif self.parent and self.parent.type != 'dir':
                    self.image = util.getimage(os.path.dirname(self.filename)+\
                                               '/cover', self.image)
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
            if not self.name:
                self.name = util.getname(self.filename)

        else:
            self.network_play = True
            self.filename     = ''
            self.mimetype     = self.type
            if not self.name:
                self.name     = Unicode(self.url)

            
    def __setitem__(self, key, value):
        """
        set the value of 'key' to 'val'
        """
        for var, val in self.autovars:
            if key == var:
                if val == value:
                    if not self.delete_info(key):
                        _debug_(u'unable to store info for \'%s\'' % self.name, 0)
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
                _debug_(u'unable to store info for \'%s\'' % self.name, 0)
        else:
            _debug_(u'unable to store info for that kind of item \'%s\'' % self.name, 0)


    def delete_info(self, key):
        """
        delete entry for metadata
        """
        if isinstance(self.info, mediainfo.Info):
            return self.info.delete(key)
        else:
            print 'unable to delete info for that kind of item'

        
    def id(self):
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

    
    def translation(self, application):
        """
        Loads the gettext translation for this item (and all it's children).
        This can be used in plugins who are not inside the Freevo distribution.
        After loading the translation, gettext can be used by self._() instead
        of the global _().
        """
        try:
            self._ = gettext.translation(application, os.environ['FREEVO_LOCALE'],
                                         fallback=1).gettext
        except:
            self._ = lambda m: m


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
                return '%d:%02d:%02d' % ( length / 3600, (length % 3600) / 60, length % 60)
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


    def getattr(self, attr):
        """
        wrapper for __getitem__ to return the attribute as string or
        an empty string if the value is 'None'
        """
        if attr[:4] == 'len(' and attr[-1] == ')':
            return self.__getitem__(attr)
        else:
            r = self.__getitem__(attr)
            return Unicode(r)
