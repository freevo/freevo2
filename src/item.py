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
# Revision 1.67  2004/02/12 17:17:08  dischi
# get image dir from skin
#
# Revision 1.66  2004/02/12 16:26:59  dischi
# fix watermark problem once and for all
#
# Revision 1.65  2004/02/08 17:39:39  dischi
# small cosmetic fixes
#
# Revision 1.64  2004/02/05 19:26:41  dischi
# fix unicode handling
#
# Revision 1.63  2004/02/05 07:17:23  gsbarbieri
# typo
#
# Revision 1.62  2004/02/05 05:44:26  gsbarbieri
# Fixes some bugs related to handling unicode internally.
# NOTE: Many of the bugs are related to using str() everywhere, so please stop doing that.
#
# Revision 1.61  2004/02/05 02:52:20  gsbarbieri
# Handle filenames internally as unicode objects.
#
# This does *NOT* affect filenames that have only ASCII chars, since the
# translation ASCII -> Unicode is painless. However this *DOES* affect files
# with accents
#
# It determines the encoding based on (in order) FREEVO_LOCALE, LANG and
# LC_ALL, which may have the form: "LANGUAGE_CODE.ENCODING",
# like "pt_BR.UTF-8"
#
# Revision 1.60  2004/02/03 20:46:57  dischi
# fix debug warning
#
# Revision 1.59  2004/02/01 19:47:13  dischi
# some fixes by using new mmpython data
#
# Revision 1.58  2004/02/01 17:08:38  dischi
# speedup, remove unneeded stuff
#
# Revision 1.57  2004/01/31 16:38:23  dischi
# changes because of mediainfo changes
#
# Revision 1.56  2004/01/31 12:38:47  dischi
# remove \0 checking, fixed mmpython
#
# Revision 1.55  2004/01/30 20:42:59  dischi
# fix name setting
#
# Revision 1.54  2004/01/24 19:14:21  dischi
# clean up autovar handling
#
# Revision 1.53  2004/01/19 20:29:11  dischi
# cleanup, reduce cache size
#
# Revision 1.52  2004/01/18 16:50:10  dischi
# (re)move unneeded variables
#
# Revision 1.51  2004/01/17 20:30:18  dischi
# use new metainfo
#
# Revision 1.50  2004/01/14 01:18:45  outlyer
# Workaround some weirdness... for some reason these should be of type None, but
# are instead the string "None" which doesn't help, since the string "None" is
# a valid string and hence not actually type None
#
# I don't think anyone who doesn't know python understands what the heck I
# just said.
#
# Revision 1.49  2004/01/11 10:57:28  dischi
# remove coming up here, it is no item attr
#
# Revision 1.48  2004/01/11 04:04:37  outlyer
# Ok,  now it shows the "Coming Up" list anywhere in the TV menu. I think
# it fits, though it looks fairly ugly right now. I'm going to make it more
# flexible after I get some listings for 'tomorrow' since mine expire tonight.
#
# I like this as a feature, but I'm wondering if someone has an idea on a
# cleaner way to implement this. This is a little hackish, since "Coming Up"
# isn't really a item "property" so it doesn't exactly fit in the object
# model.
#
# I did remove it from directory.py, so that's at least more logical.
#
# Maybe we should have a general function in item.py to call extra
# functions, or a way to embed python in the skin which isn't so nice.
#
# Ideally, we need a different way to have "default" information in an info
# area, as opposed to putting it in the item.
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

import config
from event import *
import plugin
import util

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

        self.name         = ''              # name in menu
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
            import skin
            settings  = skin.get_singleton().settings
            skin_info = settings.mainmenu.items
            imagedir  = settings.mainmenu.imagedir
            if skin_info.has_key(skin_type):
                skin_info  = skin_info[skin_type]
                self.name  = Unicode(skin_info.name)
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
                        _debug_('unable to store info for \'%s\'' % self.name, 0)
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
                _debug_('unable to store info for \'%s\'' % self.name, 0)
        else:
            _debug_('unable to store info for that kind of item \'%s\'' % self.name, 0)


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
        return the specific attribute
        """
        if attr == 'runtime':
            length = None

            if self.info['runtime'] and self.info['runtime'] != 'None':
                length = self.info['runtime']
            elif self.info['length'] and self.info['length'] != 'None':
                length = self.info['length']
            if not length and hasattr(self, 'length'):
                length = self.length
            if not length:
                return ''

            if isinstance(length, int) or isinstance(length, float) or \
                   isinstance(length, long):
                length = str(int(round(length) / 60))
            if length.find('min') == -1:
                length = '%s min' % length
            if length.find('/') > 0:
                length = length[:length.find('/')].rstrip()
            if length.find(':') > 0:
                length = length[length.find(':')+1:]
            if length == '0 min':
                return ''
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
