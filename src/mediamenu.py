#if 0 /*
# -----------------------------------------------------------------------
# mediamenu.py - Basic menu for all kinds of media
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2002/12/07 11:32:59  dischi
# Added interface.py into video/audio/image/games. The file contains a
# function cwd to return the items for the list of files. games support
# is still missing
#
# Revision 1.8  2002/12/03 19:17:05  dischi
# Added arg to all menu callback function
#
# Revision 1.7  2002/12/02 18:25:11  dischi
# Added bins/exif patch from John M Cooper
#
# Revision 1.6  2002/11/28 19:56:12  dischi
# Added copy function
#
# Revision 1.5  2002/11/26 16:28:10  dischi
# added patch for better bin support
#
# Revision 1.4  2002/11/26 12:17:57  dischi
# re-added bin album.xml support
#
# Revision 1.3  2002/11/24 19:10:19  dischi
# Added mame support to the new code. Since the hole new code is
# experimental, mame is activated by default. Change local_skin.xml
# to deactivate it after running ./cleanup
#
# Revision 1.2  2002/11/24 15:15:31  dischi
# skin.xml support re-added
#
# Revision 1.1  2002/11/24 13:58:44  dischi
# code cleanup
#
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
import util
import config
import menu
import copy
import rc
import string
import skin

from item import Item
from playlist import Playlist

import video.interface
import audio.interface
import image.interface
import games.interface

# XXX remove this when the games interface is finished
import games.mame_cache as mame_cache
from games.mameitem import MameItem

# Add support for bins album files
from image import bins

TRUE  = 1
FALSE = 0

rc = rc.get_singleton()
skin = skin.get_singleton()

class MediaMenu(Item):
    """
    This is the main menu for audio, video and images. It displays the default
    directories and the ROM_DRIVES
    """
    
    def __init__(self):
        Item.__init__(self)
        self.main_menu_selected = -1

    def main_menu_generate(self):
        """
        generate the items for the main menu. This is needed by first generating
        the menu and when something cahnges by pressing the EJECT button
        """
        items = []
        dirs  = []
        
        if self.display_type == 'video':
            dirs += config.DIR_MOVIES
        if self.display_type == 'audio':
            dirs += config.DIR_AUDIO
        if self.display_type == 'image':
            dirs += config.DIR_IMAGES
        if self.display_type == 'game':
            dirs += config.DIR_MAME

        # add default items
        for d in dirs:
            try:
                (title, dir) = d
                d = DirItem(dir, self, name = title, display_type = self.display_type)
                items += [ d ]
            except:
                # XXX catch other stuff like playlists and files here later
                pass

        # add rom drives
        for media in config.REMOVABLE_MEDIA:
            if media.info:
                # if this is a video item (e.g. DVD) and we are not in video
                # mode, deactivate it
                if media.info.type == 'video' and self.display_type != 'video':
                    m = Item(self)
                    m.type = 'video'
                    m.copy(media.info)
                    m.media = media
                    items += [ m ]
                else:
                    media.info.parent = self
                    if media.info.type == 'dir':
                        media.info.display_type = self.display_type
                    items += [ media.info ]
            else:
                m = Item(self)
                m.name = 'Drive %s (no disc)' % media.drivename
                m.media = media
                items += [ m ]

        return items



    def main_menu(self, arg=None, menuw=None):
        """
        display the (IMAGE|VIDEO|AUDIO|GAMES) main menu
        """
        self.display_type = arg
        if self.display_type == 'video':
            title = 'MOVIE'
        elif self.display_type == 'audio':
            title = 'AUDIO'
        elif self.display_type == 'image':
            title = 'IMAGE'
        elif self.display_type == 'game':
            title = 'GAMES'
        else:
            title = 'MEDIA'
        item_menu = menu.Menu('%s MAIN MENU' % title, self.main_menu_generate(),
                              umount_all=1)
        menuw.pushmenu(item_menu)



    def eventhandler(self, event = None, menuw=None):
        """
        eventhandler for the main menu. The menu must be regenerated
        when a disc in a rom drive changes
        """
        if event == rc.IDENTIFY_MEDIA:
            if not menuw:               # this shouldn't happen
                menuw = menu.get_singleton() 

            if menuw.menustack[1] == menuw.menustack[-1]:
                self.main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)

            menuw.menustack[1].choices = self.main_menu_generate()

            menuw.menustack[1].selected = menuw.menustack[1].choices[self.main_menu_selected]

            if menuw.menustack[1] == menuw.menustack[-1]:
                menuw.init_page()
                menuw.refresh()
            return TRUE

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)



    
class DirItem(Playlist):
    """
    class for handling directories
    """
    def __init__(self, dir, parent, name = '', display_type = None):
        Item.__init__(self, parent)
        self.type = 'dir'
        self.media = None
        
        # variables only for Playlist
        self.current_item = 0
        self.playlist = []
        self.autoplay = FALSE

        # variables only for DirItem
        self.dir          = dir
        self.display_type = display_type


        if name:
            self.name = name
	elif os.path.isfile(dir + '/album.xml'):
	    self.name = '[' + bins.get_bins_desc(dir)['desc']['title'] + ']'
        else:
            self.name = '[' + os.path.basename(dir) + ']'
        
        if os.path.isfile(dir+'/cover.png'): 
            self.image = dir+'/cover.png'
            if self.display_type:
                self.handle_type = self.display_type
        if os.path.isfile(dir+'/cover.jpg'): 
            self.image = dir+'/cover.jpg'
            if self.display_type:
                self.handle_type = self.display_type
            
        if os.path.isfile(dir+'/skin.xml'): 
            self.xml_file = dir+'/skin.xml'


    def copy(self, obj):
        """
        Special copy value DirItem
        """
        Playlist.copy(self, obj)
        if obj.type == 'dir':
            self.dir          = obj.dir
            self.display_type = obj.display_type
            

    def actions(self):
        return [ ( self.cwd, 'browse directory' ) ]
        
            
    def cwd(self, arg=None, menuw=None):
        """
        make a menu item for each file in the directory
        """
        
        items = []

        # are we on a ROM_DRIVE and have to mount it first?
        for media in config.REMOVABLE_MEDIA:
            if string.find(self.dir, media.mountdir) == 0:
                util.mount(self.dir)
                self.media = media

        try:
            files = [ os.path.join(self.dir, fname) for fname in os.listdir(self.dir) ]
        except OSError:
            print 'util:match_files(): Got error on dir = "%s"' % dirname
            return
            

        # build play_items for video, audio, image, games
        # the interface functions must remove the files they cover, they
        # can also remove directories

        play_items = []
        for t in ( 'video', 'audio', 'image', 'games' ):
            if not self.display_type or self.display_type == t:
                play_items += eval(t + '.interface.cwd(self, files)')
        play_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))


        # XXX BEGIN remove this when games interface is finished
        if not self.display_type or self.display_type == 'game':
            mame_list = mame_cache.getMameItemInfoList(self.dir)
            for ml in mame_list:
                play_items += [ MameItem(ml[0], ml[1], ml[2], self) ]
            self.playlist = play_items
        # XXX END remove this when games interface is finished


        # add sub-directories
        for dir in files:
            if os.path.isdir(dir):
                items += [ DirItem(dir, self, display_type = self.display_type) ]


        # playlists (only active for images and audio)
        if not self.display_type or self.display_type == 'audio':
            self.playlist = play_items

            for pl in util.find_matches(files, config.SUFFIX_AUDIO_PLAYLISTS):
                items += [ Playlist(pl, self) ]

            # random playlist
            if len(play_items) > 1 and self.display_type:
                pl = Playlist(play_items, self)
                pl.randomize()
                pl.autoplay = TRUE
                items += [ pl ]

        if not self.display_type or self.display_type == 'image':
            self.playlist = play_items

            for file in util.find_matches(files, config.SUFFIX_IMAGE_SSHOW):
                pl = Playlist(file, self)
                pl.autoplay = TRUE
                items += [ pl ]

        # add play_items to items
        items += play_items

        title = self.name
        if title[0] == '[' and title[-1] == ']':
            title = self.name[1:-1]

        # autoplay
        if len(items) == 1 and items[0].actions():
            items[0].actions()[0][0](menuw=menuw)
        else:
            item_menu = menu.Menu(title, items)
            if self.xml_file:
                item_menu.skin_settings = skin.LoadSettings(self.xml_file)

            menuw.pushmenu(item_menu)
            
