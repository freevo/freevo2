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
# Revision 1.19  2003/01/12 13:51:51  dischi
# Added the feature to remove items for videos, too. For that the interface
# was modified (update instead of remove).
#
# Revision 1.18  2003/01/11 20:09:41  dischi
# Added the self.playlist option to the directory again. This was lost
# during my adding of the last feature, sorry.
#
# Revision 1.17  2003/01/11 10:45:55  dischi
# Add a thread to watch the directory. When something changes, the update
# function will be called. The DirItem update function will add remove
# items based on the directory cahnges.
#
# Revision 1.16  2003/01/09 05:04:06  krister
# Added an option to play all movies in a dir, and generate random playlists for them.
#
# Revision 1.15  2003/01/05 11:48:53  dischi
# ignore .xvpics directories
#
# Revision 1.14  2002/12/31 04:02:18  krister
# Bugfix for mismatched variable names.
#
# Revision 1.13  2002/12/22 12:59:34  dischi
# Added function sort() to (audio|video|games|image) item to set the sort
# mode. Default is alphabetical based on the name. For mp3s and images
# it's based on the filename. Sort by date is in the code but deactivated
# (see mediamenu.py how to enable it)
#
# Revision 1.12  2002/12/11 16:06:54  dischi
# First version of a RandomPlaylist. You can access the random playlist
# from the item menu of the directory. The non-recursive random playlist
# should be added there, too, but there are some problems, so it's still
# inside the directory.
#
# Revision 1.11  2002/12/11 10:25:28  dischi
# Sort directories and playlists, too
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
from playlist import Playlist, RandomPlaylist

import video.interface
import audio.interface
import image.interface
import games.interface

# Add support for bins album files
from image import bins

TRUE  = 1
FALSE = 0

rc = rc.get_singleton()
skin = skin.get_singleton()

dirwatcher_thread = None

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
        if self.display_type == 'games':
            dirs += config.DIR_GAMES

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
        elif self.display_type == 'games':
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
        """
        return a list of actions for this item
        """
        items = [ ( self.cwd, 'Browse directory' ) ]

        # this doen't work right now because we have no playlist
        # at this point :-(
        
        # if self.playlist and len(self.playlist) > 1:
        #     items += [ (RandomPlaylist(self.playlist, self),
        #                 'Random play all items' ) ]

        if not self.display_type or self.display_type == 'audio':
            items += [ (RandomPlaylist((self.dir, config.SUFFIX_AUDIO_FILES), self),
                        'Recursive random play all items' ) ]
        return items
    

    def cwd(self, arg=None, menuw=None):
        """
        make a menu item for each file in the directory
        """
        
        # are we on a ROM_DRIVE and have to mount it first?
        for media in config.REMOVABLE_MEDIA:
            if string.find(self.dir, media.mountdir) == 0:
                util.mount(self.dir)
                self.media = media

        try:
            files = ([ os.path.join(self.dir, fname)
                       for fname in os.listdir(self.dir) ])
            self.all_files = copy.copy(files)
        except OSError:
            print 'util:match_files(): Got error on dir = "%s"' % self.dir
            return
            

        # build play_items for video, audio, image, games
        # the interface functions must remove the files they cover, they
        # can also remove directories

        play_items = []
        for t in ( 'video', 'audio', 'image', 'games' ):
            if not self.display_type or self.display_type == t:
                play_items += eval(t + '.interface.cwd(self, files)')

        if 0: # sort by date
            play_items.sort(lambda l, o: cmp(l.sort('date').upper(), o.sort('date').upper()))
        else:
            play_items.sort(lambda l, o: cmp(l.sort().upper(), o.sort().upper()))

        files.sort(lambda l, o: cmp(l.upper(), o.upper()))

        # add all playable items to the playlist of the directory
        # to play one files after the other
        if (not self.display_type or self.display_type == 'audio' or \
            self.display_type == 'image' or \
            (config.MOVIE_PLAYLISTS and self.display_type == 'video')):
            self.playlist = play_items

        # build items for sub-directories
        dir_items = []
        for dir in files:
            if os.path.isdir(dir) and os.path.basename(dir) != '.xvpics':
                dir_items += [ DirItem(dir, self, display_type = self.display_type) ]

        dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))


        # build items for playlists
        pl_items = []
        if not self.display_type or self.display_type == 'audio':
            for pl in util.find_matches(files, config.SUFFIX_AUDIO_PLAYLISTS):
                pl_items += [ Playlist(pl, self) ]

        if not self.display_type or self.display_type == 'image':
            for file in util.find_matches(files, config.SUFFIX_IMAGE_SSHOW):
                pl = Playlist(file, self)
                pl.autoplay = TRUE
                pl_items += [ pl ]

        pl_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))


        # all items together
        items = []

        # random playlist (only active for audio)
        if (not self.display_type or self.display_type == 'audio') and \
           len(play_items) > 1 and self.display_type:
            pl = Playlist(play_items, self)
            pl.randomize()
            pl.autoplay = TRUE
            items += [ pl ]

        items += dir_items + pl_items + play_items

        self.dir_items  = dir_items
        self.pl_items   = pl_items
        self.play_items = play_items


        title = self.name
        if title[0] == '[' and title[-1] == ']':
            title = self.name[1:-1]

        # autoplay
        if len(items) == 1 and items[0].actions():
            items[0].actions()[0][0](menuw=menuw)
        else:
            item_menu = menu.Menu(title, items, reload_func=self.reload)
            if self.xml_file:
                item_menu.skin_settings = skin.LoadSettings(self.xml_file)

            menuw.pushmenu(item_menu)

            global dirwatcher_thread
            if not dirwatcher_thread:
                dirwatcher_thread = DirwatcherThread(menuw)
                dirwatcher_thread.start()

            dirwatcher_thread.cwd(self, item_menu, self.dir, self.all_files)
            self.menu = item_menu


    def reload(self):
        """
        called when we return to this menu
        """
        global dirwatcher_thread
        dirwatcher_thread.cwd(self, self.menu, self.dir, self.all_files)
        dirwatcher_thread.scan()

        # we changed the menu, don't build a new one
        return None

        
    def update(self, new_files, del_files, all_files):
        """
        update the current item set. Maybe this function can share some code
        with cwd in the future, but it's easier now the way it is
        """
        new_items = []
        del_items = []

        self.all_files = all_files

        # check modules if they know something about the deleted/new files
        for t in ( 'video', 'audio', 'image', 'games' ):
            if not self.display_type or self.display_type == t:
                eval(t + '.interface.update')(self, new_files, del_files, \
                                              new_items, del_items, self.play_items)
                
        # delete play items from the menu
        for i in del_items:
            self.menu.delete_item(i)
            self.play_items.remove(i)

        # delete dir items from the menu
        for dir in del_files:
            for item in self.dir_items:
                if item.dir == dir:
                    self.menu.delete_item(item)
                    self.dir_items.remove(item)

        # delete playlist items from the menu
        for pl in del_files:
            for item in self.pl_items:
                if item.filename == pl:
                    self.menu.delete_item(item)
                    self.pl_items.remove(item)


                    
        # add new play items to the menu
        if new_items:
            self.play_items += new_items
            if 0: # sort by date
                self.play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                                      o.sort('date').upper()))
            else:
                self.play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                                      o.sort().upper()))
                

        # add new dir items to the menu
        new_dir_items = []
        for dir in new_files:
            if os.path.isdir(dir) and os.path.basename(dir) != '.xvpics':
                new_dir_items += [ DirItem(dir, self, display_type = self.display_type) ]

        if new_dir_items:
            self.dir_items += new_dir_items
            self.dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))


        # add new playlist items to the menu
        new_pl_items = []
        if not self.display_type or self.display_type == 'audio':
            for pl in util.find_matches(new_files, config.SUFFIX_AUDIO_PLAYLISTS):
                new_pl_items += [ Playlist(pl, self) ]

        if not self.display_type or self.display_type == 'image':
            for file in util.find_matches(new_files, config.SUFFIX_IMAGE_SSHOW):
                pl = Playlist(file, self)
                pl.autoplay = TRUE
                new_pl_items += [ pl ]

        if new_pl_items:
            self.pl_items += new_pl_items
            self.pl_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))


        
        items = []

        # random playlist (only active for audio)
        if (not self.display_type or self.display_type == 'audio') and \
           len(self.play_items) > 1 and self.display_type:

            # some files changed, rebuild playlist
            if new_items or del_items:
                pl = Playlist(play_items, self)
                pl.randomize()
                pl.autoplay = TRUE
                items += [ pl ]

            # reuse old playlist
            else:
                items += self.menu.choices[0]


        # build a list of all items
        items += self.dir_items + self.pl_items + self.play_items

        # finally add the items
        for i in new_items + new_dir_items + new_pl_items:
            self.menu.add_item(i, items.index(i))
                    
        # reload the menu, use an event to avoid problems because this function
        # was called by a thread
        rc.post_event(rc.REBUILD_SCREEN)




import threading
import thread
import time

class DirwatcherThread(threading.Thread):
                
    def __init__(self, menuw):
        threading.Thread.__init__(self)
        self.item = None
        self.menuw = menuw
        self.item_menu = None
        self.dir = None
        self.files = None
        self.lock = thread.allocate_lock()
        
    def cwd(self, item, item_menu, dir, files):
        self.lock.acquire()

        self.item = item
        self.item_menu = item_menu
        self.dir = dir
        self.files = files

        self.lock.release()

    def scan(self):
        self.lock.acquire()
        
        files = ([ os.path.join(self.dir, fname)
                   for fname in os.listdir(self.dir) ])
        new_files = []
        del_files = []
        
        for f in files:
            if not f in self.files:
                new_files += [ f ]
        for f in self.files:
            if not f in files:
                del_files += [ f ]

        if new_files or del_files:
            print 'directory has changed'
            self.item.update(new_files, del_files, files)
                    
        self.files = files
        self.lock.release()
        
    def run(self):
        while 1:
            if self.dir and self.menuw and self.menuw.menustack[-1] == self.item_menu and \
               not rc.app:
                self.scan()
            time.sleep(2)

    
