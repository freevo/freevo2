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
# Revision 1.65  2003/07/20 17:46:59  dischi
# special handling if there is a DVD_PLAYER plugin
#
# Revision 1.64  2003/07/19 11:45:11  dischi
# moved mmpython parsing to VideoItem
#
# Revision 1.63  2003/07/13 13:11:17  dischi
# show xml info on variants, too
#
# Revision 1.62  2003/07/07 21:56:24  dischi
# preserve mmpython info
#
# Revision 1.61  2003/07/07 21:39:50  dischi
# add special handling for mmpython video informations
#
# Revision 1.60  2003/07/05 15:53:25  outlyer
# Quiet some debugging stuff.
#
# Revision 1.59  2003/07/02 20:08:36  dischi
# make variants the default action
#
# Revision 1.58  2003/06/29 21:31:55  gsbarbieri
# subtitle and audio now use the path to files and are quoted.
#
# Revision 1.57  2003/06/29 20:43:30  dischi
# o mmpython support
# o mplayer is now a plugin
#
# Revision 1.56  2003/06/28 02:01:58  outlyer
# Mplayer won't play a file on a CD rom if -dvd-device is specified and it isn't a
# DVD rom drive, so just pass -dvd-device if playing an actual DVD.
#
# Revision 1.55  2003/06/20 19:38:31  dischi
# moved getattr to item.py
#
# Revision 1.54  2003/06/20 18:46:53  dischi
# set menu type to video and info_item type to track for DVD/VCD menu
#
# Revision 1.53  2003/06/20 17:48:01  dischi
# Title menu is now the default action for DVD/VCD. Autoplay is done by
# pressing PLAY and not SELECT. This file is also prepared for the use of
# mmpython.
#
# Revision 1.52  2003/06/07 11:32:17  dischi
# added id to find the item if it changes
#
# Revision 1.51  2003/05/27 17:53:36  dischi
# Added new event handler module
#
# Revision 1.50  2003/05/05 21:11:15  dischi
# save video width and height
#
# Revision 1.49  2003/05/05 15:14:55  outlyer
# Fixed a crash in the bookmarks submenu, and fixed the long standing bug
# where times greater than 999 seconds (16m39s) wouldn't be recorded, because
# mplayer logs time like this:
#
# A: XXX
#
# but after it reaches 1000,
#
# A:XXXX
#
# and the regular expression that got the time used a space.
#
# Revision 1.48  2003/05/04 11:52:51  dischi
# small sort bugfix
#
# Revision 1.47  2003/04/26 16:46:25  dischi
# added refresh bugfix from Matthieu Weber
#
# Revision 1.46  2003/04/26 16:38:57  dischi
# added patch from Matthieu Weber for mplayer options in disc
#
# Revision 1.45  2003/04/24 19:56:43  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.44  2003/04/24 19:22:10  dischi
# xml_file fix again
#
# Revision 1.39  2003/04/20 17:36:50  dischi
# Renamed TV_SHOW_IMAGE_DIR to TV_SHOW_DATA_DIR. This directory can contain
# images like before, but also fxd files for the tv show with global
# informations (plot/tagline/etc) and mplayer options.
#
# Revision 1.37  2003/04/20 12:43:34  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.35  2003/04/14 14:14:14  gsbarbieri
# Fix crash when using "Change Play Settings" with files instead of VCD/DVD/...
#
# Revision 1.33  2003/04/12 18:30:04  dischi
# add support for audio/subtitle selection for avis, too
#
# Revision 1.23  2003/03/19 05:40:58  outlyer
# Bugfixes to the 'bookmark' facility.
#
# 1. Why was I opening the file twice?
# 2. Clobboring the sub_item variable for use as a temporary holder was a bad idea.
# 3. Likewise, I shouldn't have clobbered file.filename in the bookmark function.
# 4. This wasn't working properly for single AVI files, only for XML-style movies.
#
# I've tried it some more, and while I think it works well enough, we really need a way to
# provide feedback. I don't actually know how without trying to use bmovl which might be
# too much.
#
# I think I may resurrect Krister's slave mode code to pass text to the screen.
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
                                     file[len(parent.media.mountdir)+1:])
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
            show_name = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(self.name))
            self.name = show_name[0] + " " + show_name[1] + "x" + show_name[2] +\
                         " - " + show_name[3] 

            if os.path.isfile((config.TV_SHOW_DATA_DIR + show_name[0] + ".png").lower()):
                self.image = (config.TV_SHOW_DATA_DIR + show_name[0] + ".png").lower()
            elif os.path.isfile((config.TV_SHOW_DATA_DIR + show_name[0] + ".jpg").lower()):
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
        items = [ (self.play, 'Play'), (self.settings, 'Change play settings') ]
        if self.filename and self.mode == 'file' and not self.media:
            items += [ (self.confirm_delete, 'Delete file') ]

        if self.variants:
            items = [ (self.show_variants, 'Show variants') ] + items

        # show DVD/VCD title menu for DVDs, but only when we aren't in a
        # submenu of a such a menu already
        if not self.filename or self.filename == '0':
            if self.mode == 'dvd':
                title_list = ( self.dvd_vcd_title_menu, 'DVD title list' )
                if plugin.getbyname(plugin.DVD_PLAYER):
                    items = [ items[0], title_list ] + items[1:]
                else:
                    items = [ title_list ] + items
            if self.mode == 'vcd':
                items = [( self.dvd_vcd_title_menu, 'VCD title list' )] + items
            for m in self.subitems:
                # Allow user to watch one of the subitems instead of always both
                # XXX Doesn't work
                #items += [( self.play, 'Play %s' % (os.path.basename(m.filename)))] 
                if os.path.exists(util.get_bookmarkfile(m.filename)):
                    myfilename = util.get_bookmarkfile(m.filename)
                    self.bookmarkfile = myfilename
                    items += [( self.bookmark_menu, 'Bookmarks')]
                    # % (os.path.basename(m.filename)))]
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
        os.remove(self.filename)
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

        if self.filename == '0' and self.mode == 'dvd' and \
               plugin.getbyname(plugin.DVD_PLAYER):
            plugin.getbyname(plugin.DVD_PLAYER).play(self)
            return
        
        if self.subitems:
            self.current_subitem = self.subitems[0]
            # Pass along the options, without loosing the subitem's own
            # options
            if self.current_subitem.mplayer_options:
                if self.mplayer_options:
                    self.current_subitem.mplayer_options += ' ' + self.mplayer_opions
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

        file = self.filename
        if self.mode == "file":
            if self.media_id:
                mountdir, file = util.resolve_media_mountdir(self.media_id,file)
                if mountdir:
                    util.mount(mountdir)
                else:
                    # TODO: prompt for the right media
                    AlertBox(text = 'Media not found for file %s' % (file)).show()
                    rc.post_event(em.PLAY_END)
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

        error = self.video_player.play(file, mplayer_options, self)

        if error:
            AlertBox(text=error).show()
            rc.post_event(em.PLAY_END)


    def stop(self, arg=None, menuw=None):
        """
        stop playing
        """
        self.video_player.stop()


    def dvdnav(self, arg=None, menuw=None):
        """
        dvdnav support, it's also still buggy in mplayer
        """
        
        self.parent.current_item = self
        mplayer_options = self.mplayer_options

        mplayer_options += ' -dvd-device %s' % self.media.devicename

        if self.selected_subtitle:
            mplayer_options += ' -sid %s' % self.selected_subtitle

        if self.selected_audio:
            mplayer_options += ' -aid %s' % self.selected_audio

        if arg:
            mplayer_options += ' %s' % arg

        if not self.menuw:
            self.menuw = menuw

        if self.menuw.visible:
            self.menuw.hide()

        error = self.video_player.play('', mplayer_options, self, 'dvdnav')

        if error:
            self.menuw.show()
            info = AlertBox(self.menuw, 'error')
            info.show()
            #info.destroy()
            rc.post_event(em.PLAY_END)

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
            min = int(sec/60)
            sec = int(sec%60)
            time = '%0.2d:%0.2d:%0.2d' % (hour,min,sec)
            file.name = 'Jump to %s' % (time)
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


        #
        # Done scanning the disc, set up the menu.
        #

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
        confmenu = configure.get_main_menu(self, self.menuw, self.xml_file)
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
        return Item.eventhandler(self, event, menuw)
