#if 0 /*
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
# Revision 1.46  2004/01/10 13:14:17  dischi
# o set self.fxd_file to None as default. It's very confusing to have one
#   fxd_file, but maybe different files with skin settings, so I added
# o self.skin_fxd to point to the updated skin informations
# o add runtime attribute
#
# Revision 1.45  2004/01/08 17:03:31  rshortt
# Bugfix for outicons.
#
# Revision 1.44  2004/01/07 18:13:25  dischi
# respect overlay files and create dir if needed
#
# Revision 1.43  2004/01/04 18:19:16  dischi
# fix len() calc
#
# Revision 1.42  2004/01/04 10:20:05  dischi
# fix missing DIRECTORY_USE_MEDIAID_TAG_NAMES for all kinds of parents
#
# Revision 1.41  2004/01/01 16:47:31  dischi
# do not replace name with None
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
#endif

import os
import gettext
import shutil
import mmpython

import config
from event import *
import plugin
import util

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
            if os.path.isdir(f):
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
        self.name         = ''              # name in menu
        self.icon         = None
        if info:
            self.info     = info
        else:
            self.info     = {}
        self.parent       = parent          # parent item to pass unmapped event
        self.menuw        = None
        self.description  = ''

        self.eventhandler_plugins = []

        if info and parent and hasattr(parent, 'DIRECTORY_USE_MEDIAID_TAG_NAMES') and \
               parent.DIRECTORY_USE_MEDIAID_TAG_NAMES and hasattr(self.info, 'title'):
            self.name = self.info['title']
        
        if parent:
            self.image = parent.image
            if self.image and isinstance(self.image, str) and \
                   self.image.startswith(config.IMAGE_DIR) and \
                   self.image.find('watermark') > 0:
                self.image = None
            self.handle_type = parent.handle_type
            self.skin_fxd    = parent.skin_fxd
            self.media       = parent.media
            if hasattr(parent, '_'):
                self._ = parent._
        else:
            self.image        = None            # imagefile
            self.skin_fxd     = None            # skin informationes etc.
            self.handle_type  = None            # handle item in skin as video, audio, image
                                                # e.g. a directory has all video info like
                                                # directories of a cdrom
            self.media        = None

                
        self.fxd_file = None

        if skin_type:
            import skin
            settings  = skin.get_singleton().settings
            skin_info = settings.mainmenu.items
            if skin_info.has_key(skin_type):
                skin_info  = skin_info[skin_type]
                self.name  = skin_info.name
                self.image = skin_info.image
                if skin_info.icon:
                    self.icon = os.path.join(settings.icon_dir, skin_info.icon)
                if skin_info.outicon:
                    self.outicon = os.path.join(settings.icon_dir, skin_info.outicon)
            


    def set_url(self, url, info=True, search_image=True):
        """
        Set a new url to the item and adjust all attributes depending
        on the url.
        """
        self.network_play = True        # network url, like http
        self.url          = url         # the url itself
        self.filename     = ''          # filename if it's a file:// url
        self.media_id     = ''

        if not url:
            self.mode     = ''          # the type of the url (file, http, dvd...)
            self.files    = None        # FileInformation
            self.mimetype = ''          # extention or mode
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
            if os.path.exists(self.filename):
                self.files.append(self.filename)
                if search_image:
                    image = util.getimage(self.filename[:self.filename.rfind('.')])
                    if image:
                        self.image = image
                        self.files.image = image
                    elif self.parent and self.parent.type != 'dir':
                        self.image = util.getimage(os.path.dirname(self.filename)+\
                                                   '/cover', self.image)

            else:
                self.filename = ''
                self.url      = ''
                self.mimetype = ''
                return

            try:
                self.mimetype = self.filename[self.filename.rfind('.')+1:].lower()
            except:
                self.mimetype = self.type

        elif self.network_play:
            self.mimetype = self.type
        else:
            self.mimetype = self.mode

            
        if info and self.filename:
            if self.parent and self.parent.media:
                mmpython_url = 'cd://%s:%s:%s' % (self.parent.media.devicename,
                                                  self.parent.media.mountdir,
                                                  self.filename[len(self.media.mountdir)+1:])
            else:
                mmpython_url = self.filename
            info = mmpython.parse(mmpython_url)
            if info:
                self.info = info
                if self.parent and \
                       hasattr(self.parent, 'DIRECTORY_USE_MEDIAID_TAG_NAMES') and \
                       self.parent.DIRECTORY_USE_MEDIAID_TAG_NAMES and \
                       hasattr(info, 'title'):
                    self.name = info['title']
        
        if not self.name:
            if self.filename:
                self.name = util.getname(self.filename)
            else:
                self.name = self.url


    def id(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        if hasattr(self, 'url'):
            return self.url
        return self.name

    
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

        else:
            if event in (STOP, PLAY_END, USER_END) and menuw:
                if menuw.visible:
                    menuw.refresh()
                else:
                    menuw.show()
                return True

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
        return the specific attribute as string or an empty string
        """
        if attr == 'runtime':
            length = None
            if self.info and hasattr(self.info, 'runtime'):
                length = self.info['runtime']
            if not length and self.info and hasattr(self.info, 'length'):
                length = self.info['length']
            if not length and self.info and hasattr(self.info, 'video') and \
                   self.info['video']:
                length = self.info['video'][0]['length']
            if not length and hasattr(self, 'length'):
                length = self.length
            if not length:
                return ''
            if isinstance(length, int) or isinstance(length, float):
                length = str(int(length) / 60)
            if length.find('min') == -1:
                length = '%s min' % length
            if length.find('/') > 0:
                length = length[:length.find('/')].rstrip()
            if length.find(':') > 0:
                length = length[length.find(':')+1:]
            return length

        
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

        if attr[:4] == 'len(' and attr[-1] == ')':
            r = None
            if self.info and self.info.has_key(attr[4:-1]):
                r = self.info[attr[4:-1]]

            if not r and hasattr(self, attr[4:-1]):
                r = getattr(self,attr[4:-1])
                
            if r != None:
                return len(r)
            return 0

        else:
            r = None
            try:
                r = self.info[attr]
            except:
                pass
            if not r:
                try:
                    r = getattr(self,attr)
                except:
                    pass
                
            if r != None and str(r):
                return str(r)
        return ''


    def getattr(self, attr):
        """
        wrapper for __getitem__
        """
        return self.__getitem__(attr)
