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

from video import xml_parser
import games.mame_cache as mame_cache

from item import Item
from video.videoitem import VideoItem
from audio.audioitem import AudioItem
from image.imageitem import ImageItem
from games.mameitem import MameItem

from playlist import Playlist

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
            title = 'MOVIE'
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
        self.dir = dir
        self.display_type = display_type
        self.media = None
        
        if name:
            self.name = name
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

        # playlist stuff
        self.current_item = 0
        self.playlist = []


    def actions(self):
        return [ ( self.cwd, 'browse directory' ) ]
        
            
    def cwd(self, menuw=None):
        """
        make a menu item for each file in the directory
        """
        
        items = []
        play_items = []
        
        # are we on a ROM_DRIVE and have to mount it first?
        for media in config.REMOVABLE_MEDIA:
            if string.find(self.dir, media.mountdir) == 0:
                util.mount(self.dir)
                self.media = media

        # add subdirs
        for dir in util.getdirnames(self.dir):
            items += [ DirItem(dir, self, display_type = self.display_type) ]


        # video items
        if not self.display_type or self.display_type == 'video':
            video_files = util.match_files(self.dir, config.SUFFIX_MPLAYER_FILES)

            for file in util.match_files(self.dir, config.SUFFIX_FREEVO_FILES):
                x = xml_parser.parseMovieFile(file, self, video_files)
                if x:
                    play_items += x

            for file in video_files:
                play_items += [ VideoItem(file, self) ]


        # audio items and audio playlists
        if not self.display_type or self.display_type == 'audio':
            for pl in util.match_files(self.dir, config.SUFFIX_AUDIO_PLAYLISTS):
                items += [ Playlist(pl, self) ]

            audio_files = util.match_files(self.dir, config.SUFFIX_AUDIO_FILES)

            for file in audio_files:
                play_items += [ AudioItem(file, self) ]

            self.playlist = play_items

            # random playlist
            if len(play_items) > 1 and self.display_type:
                pl = Playlist(play_items, self)
                pl.randomize()
                pl.autoplay = TRUE
                items += [ pl ]


        # image items and image slideshows
        if not self.display_type or self.display_type == 'image':
            for file in util.match_files(self.dir, config.SUFFIX_IMAGE_FILES):
                play_items += [ ImageItem(file, self) ]
            self.playlist = play_items
            
            for file in util.match_files(self.dir, config.SUFFIX_IMAGE_SSHOW):
                pl = Playlist(file, self)
                pl.autoplay = TRUE
                items += [ pl ]

         
        # games, right now just mame items
        if not self.display_type or self.display_type == 'game':
 
            mame_list = mame_cache.getMameItemInfoList(self.dir)
 
            print "mame_list: %s" % mame_list
            for ml in mame_list:
                # ml contains: title, file, image
                play_items += [ MameItem(ml[0], ml[1], ml[2], self) ]
 
            self.playlist = play_items
             
       
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
            
