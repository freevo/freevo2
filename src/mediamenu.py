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
# Revision 1.42  2003/03/29 21:45:26  dischi
# added display_type tv for the new skin
#
# Revision 1.41  2003/03/15 17:19:44  dischi
# renamed skin.xml to folder.fxd for the new skin
#
# Revision 1.40  2003/03/15 17:13:22  dischi
# store rom drive type in media
#
# Revision 1.39  2003/03/02 19:01:16  dischi
# removed [] from the directory name
#
# Revision 1.38  2003/02/25 05:31:48  krister
# Made CD audio playing use -cdrom-device for mplayer.
#
# Revision 1.37  2003/02/24 05:17:18  krister
# Fixed a bug in the update function.
#
# Revision 1.36  2003/02/23 09:24:31  dischi
# Activate extended menu in the (VIDEO|AUDIO|IMAGE|GAMES) menu, too
#
# Revision 1.35  2003/02/22 07:13:19  krister
# Set all sub threads to daemons so that they die automatically if the main thread dies.
#
# Revision 1.34  2003/02/21 05:27:28  krister
# Ignore CVS dirs.
#
# Revision 1.33  2003/02/21 05:00:23  krister
# Don't display .pics folders
#
# Revision 1.32  2003/02/19 13:04:32  dischi
# Only active the new auto-cover for audio
#
# Revision 1.31  2003/02/19 07:16:11  krister
# Matthieu Weber's patch for smart music cover search, modified the logic slightly.
#
# Revision 1.30  2003/02/18 05:51:21  gsbarbieri
# now we add '[' and ']' to dirname ([dirname]) only if the menu is in the old display mode. (But you must toggle the extended menu mode *before* enter the desired dir)
#
# Revision 1.29  2003/02/15 04:03:02  krister
# Joakim Berglunds patch for finding music/movie cover pics.
#
# Revision 1.28  2003/02/15 03:31:59  krister
# Joakim Berglunds patch for disabling audio random playlists.
#
# Revision 1.27  2003/02/12 10:38:51  dischi
# Added a patch to make the current menu system work with the new
# main1_image.py to have an extended menu for images
#
# Revision 1.26  2003/02/12 06:33:21  krister
# Cosmetic changes.
#
# Revision 1.25  2003/02/11 06:53:01  krister
# Fixed small bugs.
#
# Revision 1.24  2003/02/08 23:31:37  gsbarbieri
# hanged the Image menu to ExtendedMenu.
#
# OBS:
#    main1_tv: modified to handle the <indicator/> as a dict
#    xml_skin: modified to handle <indicator/> as dict and the new tag, <img/>
#    main: modified to use the ExtendedMenu
#    mediamenu: DirItem.cmd() now return items, so we can use it without a menu
#
# Revision 1.23  2003/02/04 13:14:12  dischi
# o fixed some problems with the eventhandler (and cleaned up that part)
# o DirectoryItem now reads skin.xml to get personal settings for the
#   variables MOVIE_PLAYLISTS, DIRECTORY_SORT_BY_DATE and
#   DIRECTORY_AUTOPLAY_SINGLE_ITEM
# o reformat to 80 chars/line
#
# Revision 1.22  2003/01/21 14:16:53  dischi
# Fix to avoid a crash if bins fails (xml parser broken or invalid xml file)
#
# Revision 1.21  2003/01/18 10:27:45  dischi
# Go up one menu when freevo can't read the current directory anymore. Since
# it may be inside a thread or it happens when freevo rebuilds the menu, scan
# sends rc.EXIT to go back instead of going back one menu itself.
#
# Revision 1.20  2003/01/14 18:54:26  dischi
# Added gphoto support from Thomas Sch�ppel. You need gphoto and the
# Python bindings to get this working. I added try-except to integrate
# this without breaking anything.
#
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
# Added an option to play all movies in a dir, and generate random playlists
# for them.
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
import traceback
import re

import util
import config
import menu as menu_module
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

# XML support
from xml.utils import qp_xml
            
try:
    import image.camera
    USE_CAMERA = 1
except ImportError:
    USE_CAMERA = 0

    
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
        self.type = 'mediamenu'

    def main_menu_generate(self):
        """
        generate the items for the main menu. This is needed when first generating
        the menu and if something changes by pressing the EJECT button
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
                d = DirItem(dir, self, name = title,
                            display_type = self.display_type)
                items += [ d ]
            except:
                traceback.print_exc()

        # DigiCam
        if USE_CAMERA:
            cams = image.camera.detectCameras( )
            for c in cams:
                m = image.camera.cameraFactory( self, c[0], c[1] )
                m.type = 'camera'
                m.name = c[0]
                items += [ m ]

        # add rom drives
        for media in config.REMOVABLE_MEDIA:
            if media.info:
                # if this is a video item (e.g. DVD) and we are not in video
                # mode, deactivate it
                if media.info.type == 'video' and self.display_type != 'video':
                    m = Item(self)
                    m.type = media.info.type
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
                media.info = m
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
        item_menu = menu_module.Menu('%s MAIN MENU' % title, self.main_menu_generate(),
                                     item_types = self.display_type, umount_all=1)
        menuw.pushmenu(item_menu)



    def eventhandler(self, event = None, menuw=None):
        """
        eventhandler for the main menu. The menu must be regenerated
        when a disc in a rom drive changes
        """
        if event == rc.IDENTIFY_MEDIA:
            if not menuw:               # this shouldn't happen
                menuw = menu_module.get_singleton() 

            menu = menuw.menustack[1]

            sel = menu.choices.index(menu.selected)
            menuw.menustack[1].choices = self.main_menu_generate()
            menu.selected = menu.choices[sel]

            if menu == menuw.menustack[-1] and not rc.app:
                menuw.init_page()
                menuw.refresh()
            return TRUE

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)



# ======================================================================
    
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

        # set directory variables to default
	all_variables = ('MOVIE_PLAYLISTS', 'DIRECTORY_SORT_BY_DATE',
                         'DIRECTORY_AUTOPLAY_SINGLE_ITEM', 'COVER_DIR',
                         'AUDIO_RANDOM_PLAYLIST')
        for v in all_variables:
            setattr(self, v, eval('config.%s' % v))

        if name:
            self.name = name
	elif os.path.isfile(dir + '/album.xml'):
            try:
                self.name = bins.get_bins_desc(dir)['desc']['title']
            except:
                self.name = os.path.basename(dir)
        else:
            self.name = os.path.basename(dir)

        # Check for cover in COVER_DIR
        if os.path.isfile(config.COVER_DIR+os.path.basename(dir)+'.png'):
            self.image = config.COVER_DIR+os.path.basename(dir)+'.png'
            if self.display_type:
                self.handle_type = self.display_type
        if os.path.isfile(config.COVER_DIR+os.path.basename(dir)+'.jpg'):
            self.image = config.COVER_DIR+os.path.basename(dir)+'.jpg'
            if self.display_type:
                self.handle_type = self.display_type

        # Check for a cover in current dir, overide COVER_DIR if needed
        if os.path.isfile(dir+'/cover.png'): 
            self.image = dir+'/cover.png'
            if self.display_type:
                self.handle_type = self.display_type
        if os.path.isfile(dir+'/cover.jpg'): 
            self.image = dir+'/cover.jpg'
            if self.display_type:
                self.handle_type = self.display_type
            
        if not self.image and self.display_type == 'audio':
            images = ()
            covers = ()
            files =()
            def image_filter(x):
                return re.match('.*(jpg|png)$', x, re.IGNORECASE)
            def cover_filter(x):
                return re.search(config.AUDIO_COVER_REGEXP, x, re.IGNORECASE)

            # Pick an image if it is the only image in this dir, or it matches
            # the configurable regexp
            try:
                files = os.listdir(dir)
            except OSError:
                print "oops, os.listdir() error"
                traceback.print_exc()
            images = filter(image_filter, files)
            image = None
            if len(images) == 1:
                image = os.path.join(dir, images[0])
            elif len(images) > 1:
                covers = filter(cover_filter, images)
                if covers:
                    image = os.path.join(dir, covers[0])
            self.image = image

        if config.NEW_SKIN:
            if os.path.isfile(dir+'/folder.fxd'): 
                self.xml_file = dir+'/folder.fxd'
        else:
            if os.path.isfile(dir+'/skin.xml'): 
                self.xml_file = dir+'/skin.xml'

        # set variables to values in xml file
        if self.xml_file and os.path.isfile(self.xml_file):
            try:
                parser = qp_xml.Parser()
                var_def = parser.parse(open(self.xml_file).read())
            except:
                print "Skin XML file %s corrupt" % self.xml_file
                traceback.print_exc()
                return

            for top in var_def.children:
                if top.name == 'variables':
                    for var_names in top.children:
                        for v in all_variables:
                            if var_names.name.upper() == v.upper():
                                setattr(self, v, int(var_names.textof()))


        if self.DIRECTORY_SORT_BY_DATE == 2 and self.display_type != 'tv':
            self.DIRECTORY_SORT_BY_DATE = 0

            
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

        if ((not self.display_type or self.display_type == 'audio') and
            config.AUDIO_RANDOM_PLAYLIST == 1):
            items += [ (RandomPlaylist((self.dir, config.SUFFIX_AUDIO_FILES),
                                       self),
                        'Recursive random play all items') ]
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

        if self.display_type == 'tv':
            play_items += video.interface.cwd(self, files)
            
        if self.DIRECTORY_SORT_BY_DATE:
            play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                             o.sort('date').upper()))
        else:
            play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                             o.sort().upper()))

        files.sort(lambda l, o: cmp(l.upper(), o.upper()))

        # add all playable items to the playlist of the directory
        # to play one files after the other
        if (not self.display_type or self.display_type == 'audio' or \
            self.display_type == 'image' or \
            (self.MOVIE_PLAYLISTS and self.display_type == 'video')):
            self.playlist = play_items

        # build items for sub-directories
        dir_items = []
        for filename in files:
            if (os.path.isdir(filename) and
                os.path.basename(filename) != 'CVS' and
                os.path.basename(filename) != '.xvpics' and
                os.path.basename(filename) != '.pics'):
                dir_items += [ DirItem(filename, self, display_type =
                                       self.display_type) ]

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
        if ((not self.display_type or self.display_type == 'audio') and \
            len(play_items) > 1 and self.display_type and
            config.AUDIO_RANDOM_PLAYLIST == 1):
            pl = Playlist(play_items, self)
            pl.randomize()
            pl.autoplay = TRUE
            items += [ pl ]

        items += dir_items + pl_items + play_items

        self.dir_items  = dir_items
        self.pl_items   = pl_items
        self.play_items = play_items


        title = self.name

        # autoplay
        if len(items) == 1 and items[0].actions() and \
           self.DIRECTORY_AUTOPLAY_SINGLE_ITEM:
            items[0].actions()[0][0](menuw=menuw)
        else:
            item_menu = menu_module.Menu(title, items, reload_func=self.reload,
                                         item_types = self.display_type)
            if self.xml_file:
                item_menu.skin_settings = skin.LoadSettings(self.xml_file)

            if menuw:
                menuw.pushmenu(item_menu)

            global dirwatcher_thread
            if not dirwatcher_thread:
                dirwatcher_thread = DirwatcherThread(menuw)
                dirwatcher_thread.setDaemon(1)
                dirwatcher_thread.start()

            dirwatcher_thread.cwd(self, item_menu, self.dir, self.all_files)
            self.menu = item_menu

        return items

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
                                              new_items, del_items, \
                                              self.play_items)
                
        if self.display_type == 'tv':
            video.interface.update(self, new_files, del_files, 
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
            if self.DIRECTORY_SORT_BY_DATE:
                self.play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                                      o.sort('date').upper()))
            else:
                self.play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                                      o.sort().upper()))
                

        # add new dir items to the menu
        new_dir_items = []
        for dir in new_files:
            if (os.path.isdir(dir) and
                os.path.basename(dir) != 'CVS' and
                os.path.basename(dir) != '.xvpics' and
                os.path.basename(dir) != '.pics'):
                new_dir_items += [ DirItem(dir, self,
                                           display_type = self.display_type) ]

        if new_dir_items:
            self.dir_items += new_dir_items
            self.dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))


        # add new playlist items to the menu
        new_pl_items = []
        if not self.display_type or self.display_type == 'audio':
            for pl in util.find_matches(new_files,
                                        config.SUFFIX_AUDIO_PLAYLISTS):
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
        if ((not self.display_type or self.display_type == 'audio') and \
            len(self.play_items) > 1 and self.display_type and
            config.AUDIO_RANDOM_PLAYLIST == 1):

            # some files changed, rebuild playlist
            if new_items or del_items:
                pl = Playlist(self.play_items, self)
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



# ======================================================================

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

        try:
            files = ([ os.path.join(self.dir, fname)
                       for fname in os.listdir(self.dir) ])
        except OSError:
            # the directory is gone
            print 'unable to read directory'

            # send EXIT to go one menu up:
            rc.post_event(rc.EXIT)
            self.lock.release()
            return
        
        
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
            if self.dir and self.menuw and \
               self.menuw.menustack[-1] == self.item_menu and \
               not rc.app:
                self.scan()
            time.sleep(2)

    
