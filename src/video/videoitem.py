#if 0 /*
# -----------------------------------------------------------------------
# videoitem.py - Item for video objects
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.75  2003/08/23 10:28:47  dischi
# fixed some variants handling
#
# Revision 1.74  2003/08/22 18:47:06  gsbarbieri
# - Added more time to retry to check for media.
# - Corrected a bug when playing variant from CD when the parent is a string
#   (the base directory). BTW: why that as parent?!
#
# Revision 1.73  2003/08/21 20:54:44  gsbarbieri
#    *ROM media just shows up when needed, ie: audiocd is not displayed in
# video main menu.
#    * ROM media is able to use variants, subtitles and more.
#    * When media is not present, ask for it and wait until media is
# identified. A better solution is to force identify media and BLOCK until
# it's done.
#
# Revision 1.72  2003/08/20 20:47:02  outlyer
# Fixed the bookmark file "parser" I don't know what happened, but it was
# completely broken for AVI files (or any file without options in local_conf)
#
# Also, the minute calculation wasn't working. I don't know why I thought
# the old one would, but this works for bookmarks > 3600
#
# Revision 1.22  2003/03/17 19:22:31  outlyer
# Bookmarks are working now.
#
# Usage:
#     1. while watching a movie file, hit the 'record' button and it'll save a
#     bookmark. There is no visual feedback though.
#     2. Later, to get back there, choose the actions button in the menu, and it'll
#     have a list of bookmarks in a submenu, click on one of those to resume from
#     where you saved.
#
#     The bookmarks do work for multiple AVI's together, though the time shown in the
#     menu will be the time for the individual file, not the aggregate.
#
# TODO:
#     For multi-part files (i.e. two AVI's together via an XML file) it would be
#     nice to be able to choose which one. I added a menu item (commented out now)
#     until I can figure out how to pass self.play a specific filename.
#
# Revision 1.21  2003/03/17 18:54:45  outlyer
# Some changes for the bookmarks
#     o videoitem.py - Added bookmark menu, bookmark "parser" and menu generation,
#             haven't figured out how to pass the timecode to mplayer though. I tried
#             setting mplayer_options, but self.play seems to just ignore them. I don't
#             know how to pass anything to self.play either. ARGH.
#     o mplayer.py - commented out two extraneous prints.
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
import re

import config
import util

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

import rc
import event as em
import menu
import time
import copy
import mmpython

from gui.PopupBox import PopupBox
from gui.AlertBox import AlertBox
from gui.ConfirmBox import ConfirmBox

from item import Item

import configure
import plugin

class VideoItem(Item):
    def __init__(self, filename, parent, info=None):
        if parent and parent.media:
            url = 'cd://%s:%s:%s' % (parent.media.devicename, parent.media.mountdir,
                                     filename[len(parent.media.mountdir)+1:])
        else:
            url = filename

        Item.__init__(self, parent, mmpython.parse(url))

        # fix values
        self.type  = 'video'
        self.handle_type = 'video'

        self.mode  = 'file'             # file, dvd or vcd
        self.media_id = ''              # if media == vcd or dvd

        self.files_options = []         # options for specific files of a
                                        # disc in a disc-set

        self.variants = []              # if this item has variants
        self.subitems = []              # if this item has more than one file/track to play
        self.current_subitem = None
        self.bookmarkfile = None

        self.subtitle_file = {}         # text subtitles
        self.audio_file = {}            # audio dubbing

        self.filename = filename
        self.id       = filename
        if not self.name:
            self.name     = util.getname(filename)
        self.basename = os.path.basename(os.path.splitext(filename)[0])
        self.tv_show  = FALSE
        self.mplayer_options = ''
        self.xml_file = None
        
        # find image for tv show and build new title
        if config.TV_SHOW_REGEXP_MATCH(self.name):
            show_name = config.TV_SHOW_REGEXP_SPLIT(self.name)
            if show_name[0] and show_name[1] and show_name[2] and show_name[3]:
                self.name = show_name[0] + " " + show_name[1] + "x" + show_name[2] +\
                             " - " + show_name[3] 
                if os.path.isfile((config.TV_SHOW_DATA_DIR + show_name[0] + ".png").lower()):
                    self.image = (config.TV_SHOW_DATA_DIR + show_name[0] + ".png").lower()
                elif os.path.isfile((config.TV_SHOW_DATA_DIR + \
                                     show_name[0] + ".jpg").lower()):
                    self.image = (config.TV_SHOW_DATA_DIR + show_name[0] + ".jpg").lower()

                if config.TV_SHOW_INFORMATIONS.has_key(show_name[0].lower()):
                    tvinfo = config.TV_SHOW_INFORMATIONS[show_name[0].lower()]
                    for i in tvinfo[1]:
                        self.info[i] = tvinfo[1][i]
                    if not self.image:
                        self.image = tvinfo[0]
                    if not self.xml_file:
                        self.xml_file = tvinfo[3]
                    self.mplayer_options = tvinfo[2]

                self.tv_show = TRUE
                self.show_name = show_name
            
        # find image for this file
        # First check in COVER_DIR
        if os.path.isfile(config.COVER_DIR+self.basename+'.png'):
            self.image = config.COVER_DIR+self.basename+'.png'
        elif os.path.isfile(config.COVER_DIR+self.basename+'.jpg'):
            self.image = config.COVER_DIR+self.basename+'.jpg'
        # Then check for episode in TV_SHOW_DATA_DIR
        if os.path.isfile(os.path.splitext(filename)[0] + ".png"):
            self.image = os.path.splitext(filename)[0] + ".png"
        elif os.path.isfile(os.path.splitext(filename)[0] + ".jpg"):
            self.image = os.path.splitext(filename)[0] + ".jpg"


        self.video_player = plugin.getbyname(plugin.VIDEO_PLAYER)

        # variables only for VideoItem
        self.label = ''
        
        self.available_audio_tracks = []
        self.available_subtitles    = []
        self.available_chapters     = 0
        self.video_width  = 0
        self.video_height = 0

        self.selected_subtitle = None
        self.selected_audio    = None
        self.num_titles        = 0
        self.deinterlace       = 0

        if parent and hasattr(self.parent, 'xml_file') and not self.xml_file:
            self.xml_file = self.parent.xml_file
            
        
    def copy(self, obj):
        """
        Special copy value VideoItems
        """
        Item.copy(self, obj)
        if obj.type == 'video':
            self.available_audio_tracks = obj.available_audio_tracks
            self.available_subtitles    = obj.available_subtitles
            self.available_chapters     = obj.available_chapters

            self.selected_subtitle = obj.selected_subtitle
            self.selected_audio    = obj.selected_audio
            self.num_titles        = obj.num_titles
            self.label             = obj.label
            self.tv_show           = obj.tv_show
            self.id                = obj.id
            
            self.variants          = obj.variants
            self.subitems          = obj.subitems
            self.files_options     = obj.files_options
            self.current_subitem   = obj.current_subitem
            self.bookmarkfile      = obj.bookmarkfile
            self.subtitle_file     = obj.subtitle_file
            self.audio_file        = obj.audio_file
            self.filename          = obj.filename




    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr in ('length', 'geometry', 'aspect'):
            try:
                video = self.info.video[0]
                if attr == 'length':
                    length = video.length
                    if length / 3600:
                        return '%d:%02d:%02d' % ( length / 3600, (length % 3600) / 60,
                                                  length % 60)
                    else:
                        return '%d:%02d' % (length / 60, length % 60)
                if attr == 'geometry':
                    return '%sx%s' % (video.width, video.height)
                if attr == 'aspect':
                    aspect = getattr(video, attr)
                    return aspect[:aspect.find(' ')].replace('/', ':')
            except:
                pass
        return Item.getattr(self, attr)
                
    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date' and os.path.isfile(self.filename):
            return '%s%s' % (os.stat(self.filename).st_ctime, self.filename)

        if self.name.find("The ") == 0:
            return self.name[4:]
        return self.name

    
    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        items = [ (self.play, 'Play'), ]
        if not self.filename or self.filename == '0':
            if self.mode == 'dvd':
                if plugin.getbyname(plugin.DVD_PLAYER):
                    items = [ (self.play, 'Play DVD'),
                              ( self.dvd_vcd_title_menu, 'DVD title list' ) ]
                else:
                    items = [ ( self.dvd_vcd_title_menu, 'DVD title list' ),
                              (self.play, 'Play default track') ]
                    
            elif self.mode == 'vcd':
                if plugin.getbyname(plugin.VCD_PLAYER):
                    items = [ (self.play, 'Play VCD'),
                              ( self.dvd_vcd_title_menu, 'VCD title list' ) ]
                else:
                    items = [ ( self.dvd_vcd_title_menu, 'VCD title list' ),
                              (self.play, 'Play default track') ]


        items += configure.get_items(self)
 
        if self.filename and self.mode == 'file' and not self.media:
            items += [ (self.confirm_delete, 'Delete file') ]


        if self.variants and len(self.variants) > 1:
            items = [ (self.show_variants, 'Show variants') ] + items

        if not self.filename or self.filename == '0':
            for m in self.subitems:
                # Allow user to watch one of the subitems instead of always both
                # XXX Doesn't work
                #items += [( self.play, 'Play %s' % (os.path.basename(m.filename)))] 
                if os.path.exists(util.get_bookmarkfile(m.filename)):
                    myfilename = util.get_bookmarkfile(m.filename)
                    self.bookmarkfile = myfilename
                    items += [( self.bookmark_menu, 'Bookmarks')]

        else:
            if os.path.exists(util.get_bookmarkfile(self.filename)):
                self.bookmarkfile = util.get_bookmarkfile(self.filename) 
                items += [( self.bookmark_menu, 'Bookmarks ')] 

        return items


    def confirm_delete(self, arg=None, menuw=None):
        if not self.menuw:
            self.menuw = menuw
        ConfirmBox(text='Do you wish to delete\n %s?' % self.name,
                   handler=self.delete_file, default_choice=1).show()


    def delete_file(self):
        if DEBUG: print 'Deleting %s' % self.filename
        base = os.path.splitext(self.filename)[0] + '.'
        if os.path.isfile(base + 'jpg'):
            os.remove(base + 'jpg')
        if os.path.isfile(base + 'png'):
            os.remove(base + 'png')
        if os.path.isfile(self.filename):
            os.unlink(self.filename)
        if hasattr(self, 'fxd_file') and os.path.isfile(self.fxd_file):
            os.unlink(self.fxd_file)
        self.menuw.back_one_menu(arg='reload')


    def show_variants(self, arg=None, menuw=None):
        if not self.menuw:
            self.menuw = menuw
        m = menu.Menu(self.name, self.variants, reload_func=None, xml_file=self.xml_file)
        m.item_types = 'video'
        self.menuw.pushmenu(m)


    def play(self, arg=None, menuw=None):
        """
        play the item.
        """
        self.parent.current_item = self

        if not self.menuw:
            self.menuw = menuw

        # dvd playback for whole dvd
        if (not self.filename or self.filename == '0') and \
               self.mode == 'dvd' and plugin.getbyname(plugin.DVD_PLAYER):
            plugin.getbyname(plugin.DVD_PLAYER).play(self)
            return

        # vcd playback for whole vcd
        if (not self.filename or self.filename == '0') and \
               self.mode == 'vcd' and plugin.getbyname(plugin.VCD_PLAYER):
            plugin.getbyname(plugin.VCD_PLAYER).play(self)
            return

        # if we have variants, play the first one as default
        if self.variants:
            self.variants[0].play(arg, menuw)
            return

        # if we have subitems (a movie with more than one file),
        # we start playing the first
        if self.subitems:
            self.current_subitem = self.subitems[0]
            # Pass along the options, without loosing the subitem's own
            # options
            if self.current_subitem.mplayer_options:
                if self.mplayer_options:
                    self.current_subitem.mplayer_options += ' ' + self.mplayer_options
            else:
                self.current_subitem.mplayer_options = self.mplayer_options
            # When playing a subitem, the menu must be hidden. If it is not,
            # the playing will stop after the first subitem, since the
            # PLAY_END/USER_END event is not forwarded to the parent
            # videoitem.
            # And besides, we don't need the menu between two subitems.
            self.menuw.hide()

            self.current_subitem.play(arg, self.menuw)
            return


        # normal plackback of one file
        file = self.filename
        if self.mode == "file":
            if self.media_id:
                mountdir, file = util.resolve_media_mountdir(self.media_id,file)
                if mountdir:
                    util.mount(mountdir)
                else:
                    
                    def do_tryagain():                        
                        # TODO: force to identify media instead of wait
                        box = PopupBox( text="Wait while detecting media..." )
                        box.show()
                        l=1
                        for i in range( 10 ): # 10 times
                            
                            for media in config.REMOVABLE_MEDIA:
                                # media has no id? maybe identifying... wait
                                if not media.id:
                                    time.sleep( 2 )
                                if media.id == self.media_id:
                                    # we found it! Stop looping
                                    l=0
                                    break
                                
                            if not l:
                                break
                        box.destroy()
                                                    
                        self.play( arg, menuw )
                    # do_tryagain()
                        
                    
                    ConfirmBox( text=('Media not found for file "%s".\n'+
                                      'Please insert the media.') % file,
                                handler=do_tryagain ).show()
                    
                    rc.post_event( em.PLAY_END )

                    return

            elif self.media:
                util.mount(os.path.dirname(self.filename))

        elif self.mode == 'dvd' or self.mode == 'vcd':
            if not self.media:
                media = util.check_media(self.media_id)
                if media:
                    self.media = media
                else:
                    AlertBox(text='Media not found for %s track %s' % \
                             (self.mode, file)).show()
                    rc.post_event(em.PLAY_END)
                    return

        if not self.filename or self.filename == '0':
            if self.mode == 'dvd':
                file = '1'
            elif self.mode == 'vcd':
                # try to get the longest track:
                try:
                    import cdrom
                    device = open(self.media.devicename)
                    (first, last) = cdrom.toc_header(device)

                    lmin = 0
                    lsec = 0

                    mainmovie = (0, 0)
                    for i in range(first, last + 2):
                        if i == last + 1:
                            min, sec, frames = cdrom.leadout(device)
                        else:
                            min, sec, frames = cdrom.toc_entry(device, i)
                        if (min-lmin) * 60 + (sec-lsec) > mainmovie[0]:
                            mainmovie = (min-lmin) * 60 + (sec-lsec), i-1
                        lmin, lsec = min, sec
                    file = str(mainmovie[1])
                    device.close()
                except:
                    file = '1'

        mplayer_options = self.mplayer_options
        if not mplayer_options:
            mplayer_options = ""

        if self.media:
            mplayer_options += ' -cdrom-device %s ' % \
                               (self.media.devicename)

        if self.mode == 'dvd':
            mplayer_options += ' -dvd-device %s' % self.media.devicename


        if self.selected_subtitle and self.mode == 'file':
            mplayer_options += ' -vobsubid %s' % self.selected_subtitle
        elif self.selected_subtitle:
            mplayer_options += ' -sid %s' % self.selected_subtitle
            
        if self.selected_audio:
            mplayer_options += ' -aid %s' % self.selected_audio

        if self.subtitle_file:
            d, f = util.resolve_media_mountdir(self.subtitle_file['media-id'],
                                               self.subtitle_file['file'])
            if d:
                util.mount(d)
            mplayer_options += ' -sub "%s"' % f

        if self.audio_file:
            d, f = util.resolve_media_mountdir(self.audio_file['media-id'],
                                               self.audio_file['file'])
            if d:
                util.mount(d)
            mplayer_options += ' -audiofile "%s"' % f

        if arg:
            mplayer_options += ' %s' % arg

        if self.deinterlace:
            mplayer_options += ' -vop pp=fd'


        if self.menuw.visible:
            self.menuw.hide()

        if not self.video_player:            
            self.video_player = plugin.getbyname(plugin.VIDEO_PLAYER)
            
        if self.video_player:
            error = self.video_player.play(file, mplayer_options, self)
        else:
            error = "No video player avaiable!"

        if error:
            AlertBox(text=error).show()
            rc.post_event(em.PLAY_END)


    def stop(self, arg=None, menuw=None):
        """
        stop playing
        """
        self.video_player.stop()


    def bookmark_menu(self,arg=None, menuw=None):
        """
        Bookmark list
        """
        bookmarkfile = self.bookmarkfile
        items = []
        for line in util.readfile(bookmarkfile):
            file = copy.copy(self)
            sec = int(line)
            hour = int(sec/3600)
            min = int((sec-(hour*3600))/60)
            sec = int(sec%60)
            time = '%0.2d:%0.2d:%0.2d' % (hour,min,sec)
            file.name = 'Jump to %s' % (time)
            if not self.mplayer_options:
                self.mplayer_options = ''
            file.mplayer_options = str(self.mplayer_options) +  ' -ss %s' % time
            items += [file]
        moviemenu = menu.Menu(self.name, items, xml_file=self.xml_file)
        menuw.pushmenu(moviemenu)
        
        return

    def dvd_vcd_title_menu(self, arg=None, menuw=None):
        """
        Generate special menu for DVD/VCD/SVCD content
        """
        if not self.menuw:
            self.menuw = menuw

        # only one track, play it
        if self.num_titles == 1:
            file = copy.copy(self)
            file.filename = '1'
            file.play(menuw = self.menuw)
            return

        # build a menu
        items = []
        for title in range(1,self.num_titles+1):
            file = copy.copy(self)

            # copy the attributes from mmpython about this track
            if self.info.has_key('tracks'):
                file.info = self.info.tracks[title-1]
            file.info_type = 'track'
            file.filename = '%s' % title
            file.name = 'Play Title %s' % title
            items += [file]

        moviemenu = menu.Menu(self.name, items, umount_all = 1, xml_file=self.xml_file)
        moviemenu.item_types = 'video'
        self.menuw.pushmenu(moviemenu)
        return


    def settings(self, arg=None, menuw=None):
        if not self.menuw:
            self.menuw = menuw
        confmenu = configure.get_menu(self, self.menuw, self.xml_file)
        self.menuw.pushmenu(confmenu)
        

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for this item
        """

        # when called from mplayer.py, there is no menuw
        if not menuw:
            menuw = self.menuw

        # DVD protected
        if event == em.DVD_PROTECTED:
            AlertBox(text='The DVD is protected, see the docs for more info!').show()
            event = em.PLAY_END

        # PLAY_END: do have have to play another file?
        if self.subitems:
            if event == em.PLAY_END:
                try:
                    pos = self.subitems.index(self.current_subitem)
                    if pos < len(self.subitems)-1:
                        self.current_subitem = self.subitems[pos+1]
                        print "playing next item"
                        self.current_subitem.play(menuw=menuw)
                        return TRUE
                except:
                    pass
            elif event == em.USER_END:
                pass

        # show configure menu
        if event == em.MENU:
            self.video_player.stop()
            self.settings(menuw=menuw)
            menuw.show()
            return TRUE
        
        # give the event to the next eventhandler in the list
        if isinstance( self.parent, str ):
            self.parent = None
        return Item.eventhandler(self, event, menuw)
