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
# Revision 1.40  2003/04/21 17:35:12  dischi
# also remove images on delete
#
# Revision 1.39  2003/04/20 17:36:50  dischi
# Renamed TV_SHOW_IMAGE_DIR to TV_SHOW_DATA_DIR. This directory can contain
# images like before, but also fxd files for the tv show with global
# informations (plot/tagline/etc) and mplayer options.
#
# Revision 1.38  2003/04/20 13:07:38  dischi
# bugfix
#
# Revision 1.37  2003/04/20 12:43:34  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.36  2003/04/19 21:27:24  dischi
# small fix
#
# Revision 1.35  2003/04/14 14:14:14  gsbarbieri
# Fix crash when using "Change Play Settings" with files instead of VCD/DVD/...
#
# Revision 1.34  2003/04/13 18:00:15  dischi
# reload menu when deleting a file
#
# Revision 1.33  2003/04/12 18:30:04  dischi
# add support for audio/subtitle selection for avis, too
#
# Revision 1.32  2003/04/06 21:13:06  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
#
# Revision 1.31  2003/03/31 20:44:53  dischi
# shorten time between pop.destroy and menu drawing
#
# Revision 1.30  2003/03/31 20:37:33  dischi
# added parent to gui popup box
#
# Revision 1.29  2003/03/31 03:04:46  rshortt
# Make the delete file confirm box default to 'cancel'.
#
# Revision 1.28  2003/03/31 03:02:35  rshortt
# Inside the item menu added the option to delete the file.  This pops up
# a confirm box to make sure.
#
# Revision 1.27  2003/03/30 18:04:46  dischi
# update to new gui interface
#
# Revision 1.26  2003/03/30 16:50:20  dischi
# pass xml_file definition to submenus
#
# Revision 1.25  2003/03/23 20:00:26  dischi
# Added patch from Matthieu Weber for better mplayer_options and subitem
# handling
#
# Revision 1.24  2003/03/22 20:03:02  dischi
# add detailed information for tv shows
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
# Revision 1.20  2003/03/16 19:28:05  dischi
# Item has a function getattr to get the attribute as string
#
# Revision 1.19  2003/03/14 16:24:33  dischi
# Patch from Matthieu Weber with some bugfixes
#
# Revision 1.18  2003/03/03 00:36:53  rshortt
# Implimenting the new PopupBox for the 'Scanning disc, be patient...' messages.
#
# Revision 1.17  2003/03/02 14:58:23  dischi
# Removed osd.clearscreen and if we have the NEW_SKIN deactivate
# skin.popupbox, refresh, etc. Use menuw.show and menuw.hide to do this.
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
import re

import config
import util
import mplayer

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

import rc
import menu
import time
import copy

from gui.PopupBox import PopupBox
from gui.AlertBox import AlertBox
from gui.ConfirmBox import ConfirmBox

from item import Item

import configure


class VideoItem(Item):
    def __init__(self, filename, parent):
        Item.__init__(self, parent)

        # fix values
        self.type  = 'video'
        self.handle_type = 'video'

        self.mode  = 'file'             # file, dvd or vcd
        self.media_id = ''              # if media == vcd or dvd

        self.variants = []              # if this item has variants
        self.subitems = []              # if this item has more than one file/track to play
        self.current_subitem = None
        self.bookmarkfile = None

        self.subtitle_file = {}         # text subtitles
        self.audio_file = {}            # audio dubbing

        self.filename = filename
        self.name    = util.getname(filename)
        self.tv_show = FALSE
        self.mplayer_options = ''
        
        # XML file infos
        # possible values are: genre, runtime, tagline, plot, year, rating
        self.info = {}

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
                self.info = tvinfo[1]
                if not self.image:
                    self.image = tvinfo[0]
                self.mplayer_options = tvinfo[2]
                
            self.tv_show = TRUE
            self.show_name = show_name
            
        # find image for this file
        # First check in COVER_DIR
        if os.path.isfile(config.COVER_DIR+self.name+'.png'):
            self.image = config.COVER_DIR+self.name+'.png'
        elif os.path.isfile(config.COVER_DIR+self.name+'.jpg'):
            self.image = config.COVER_DIR+self.name+'.jpg'
        # Then check for episode in TV_SHOW_DATA_DIR
        if os.path.isfile(os.path.splitext(filename)[0] + ".png"):
            self.image = os.path.splitext(filename)[0] + ".png"
        elif os.path.isfile(os.path.splitext(filename)[0] + ".jpg"):
            self.image = os.path.splitext(filename)[0] + ".jpg"


        self.video_player = mplayer.get_singleton()

        # variables only for VideoItem
        self.label = ''
        
        self.scanned = FALSE
        self.available_audio_tracks = []
        self.available_subtitles    = []
        self.available_chapters     = 0

        self.selected_subtitle = None
        self.selected_audio    = None
        self.num_titles        = 0
        self.deinterlace       = 0

        self.xml_file = None

        
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
            self.tv_show           = onj.tv_show


    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date' and os.path.isfile(self.filename):
            return '%s%s' % (os.stat(self.filename).st_ctime, self.filename)

        if self.name.find("The ") == 0:
            return self.name[4]
        return self.name

    
    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        a = Item.getattr(self, attr)
        if not a and self.info and self.info.has_key(attr):
            a = str(self.info[attr])
        return a

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
            items += [ (self.show_variants, 'Show variants') ]

        # show DVD/VCD title menu for DVDs, but only when we aren't in a
        # submenu of a such a menu already
        if not self.filename or self.filename == '0':
            if self.mode == 'dvd':
                items += [( self.dvdnav, 'DVD Menu (experimental)' )]
                items += [( self.dvd_vcd_title_menu, 'DVD title list' )]
            if self.mode == 'vcd':
                items += [( self.dvd_vcd_title_menu, 'VCD title list' )]
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
        print 'Deleting %s' % self.filename
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
        self.menuw.pushmenu(m)


    def play(self, arg=None, menuw=None):
        """
        play the item.
        """
        self.parent.current_item = self
        
        if not self.menuw:
            self.menuw = menuw

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
                    rc.post_event(rc.PLAY_END)
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
                    rc.post_event(rc.PLAY_END)
                    return

        if (not self.filename or self.filename == '0') and \
           (self.mode == 'dvd' or self.mode == 'vcd'):
            file = '1'

        mplayer_options = self.mplayer_options
        if not mplayer_options:
            mplayer_options = ""

        if self.media:
            mplayer_options += ' -cdrom-device %s -dvd-device %s' % \
                               (self.media.devicename, self.media.devicename)

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
            mplayer_options += ' -sub %s' % f

        if self.audio_file:
            d, f = util.resolve_media_mountdir(self.audio_file['media-id'],
                                               self.audio_file['file'])
            if d:
                util.mount(d)
            mplayer_options += ' -audiofile %s' % f

        if arg:
            mplayer_options += ' %s' % arg

        if self.deinterlace:
            mplayer_options += ' -vop pp=fd'


        if self.menuw.visible:
            self.menuw.hide()

        error = self.video_player.play(file, mplayer_options, self)

        if error:
            self.menuw.show()
            AlertBox(text=error).show()
            rc.post_event(rc.PLAY_END)


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
            rc.post_event(rc.PLAY_END)

    def bookmark_menu(self,arg=None, menuw=None):
        """
        Bookmark list
        """
        bookmarkfile = self.bookmarkfile
        items = []
        lines = open(str(bookmarkfile),'r').readlines()
        for line in lines: 
            file = copy.copy(self)
            sec = int(line)
            hour = int(sec/3600)
            min = int(sec/60)
            sec = int(sec%60)
            time = '%0.2d:%0.2d:%0.2d' % (hour,min,sec)
            file.name = 'Jump to %s' % (time)
            file.mplayer_options += " -ss %s" % (time)
            items += [file]
        
        moviemenu = menu.Menu(self.name, items, xml_file=self.xml_file)
        self.menuw.pushmenu(moviemenu)

        return





    def dvd_vcd_title_menu(self, arg=None, menuw=None):
        """
        Generate special menu for DVD/VCD/SVCD content
        """
        pop = None

        if not self.menuw:
            self.menuw = menuw

        if not self.num_titles:
            # Use the uid to make a user-unique filename
            uid = os.getuid()

            # Figure out the number of titles on this disc
            pop = PopupBox(text='Scanning disc, be patient...',
                           icon='skins/icons/misc/cdrom_mount.png')
            pop.show()

                
            os.system('rm -f /tmp/mplayer_dvd_%s.log /tmp/mplayer_dvd_done_%s' % (uid, uid))

            if self.mode == 'dvd':
                # Get the number of titles on the DVD
                probe_file = '-dvd 1'
            else:
                # play track 99 which isn't there (very sure!), scan mplayers list
                # of found tracks to get the total number of tracks
                probe_file = '-vcd 99'

            cmd = config.MPLAYER_CMD + ' -ao null -nolirc -vo null -frames 0 '
            if self.media:
                cmd += ' -cdrom-device %s -dvd-device %s' % \
                       (self.media.devicename, self.media.devicename)
            cmd += ' %s 2> /dev/null > /tmp/mplayer_dvd_%s.log' % (probe_file, uid)

            os.system(cmd + (' ; touch /tmp/mplayer_dvd_done_%s' % uid))

            timeout = time.time() + 20.0
            done = 0
            while 1:
                if time.time() >= timeout:
                    print 'DVD/VCD disc read failed!'
                    break

                if os.path.isfile('/tmp/mplayer_dvd_done_%s' % uid):
                    done = 1
                    break

            found = 0
            num_files = 0

            if done and self.mode == 'dvd':
                # Look for 'There are NNN titles on this DVD'
                lines = open('/tmp/mplayer_dvd_%s.log' % uid).readlines()
                for line in lines:
                    if line.find('titles on this DVD') != -1:
                        self.num_titles = int(line.split()[2])
                        print 'Got num_titles = %s from str "%s"' % (self.num_titles, line)
                        found = 1
                        break

            elif done:
                # Look for 'track NN'
                lines = open('/tmp/mplayer_dvd_%s.log' % uid).readlines()
                for line in lines:
                    if line.find('track ') == 0:
                        self.num_titles = int(line[6:8])
                        found = 1

                # Count the files on the VCD
                util.mount(self.media.mountdir)
                for dirname in ('/mpegav/', '/MPEG2/', '/mpeg2/'):
                    num_files += len(util.match_files(self.media.mountdir + dirname,
                                                      [ 'mpg', 'dat' ]))
                util.umount(self.media.mountdir)

            if not done or not found:
                self.num_titles = 100 # XXX Kludge

        #
        # Done scanning the disc, set up the menu.
        #

        # only one track, play it
        if self.num_titles == 1:
            file = copy.copy(self)
            file.filename = '1'
            if pop:
                pop.destroy()
            file.play(menuw = self.menuw)
            return

        # build a menu
        items = []
        for title in range(1,self.num_titles+1):
            file = copy.copy(self)
            file.filename = '%s' % title
            file.name = 'Play Title %s' % title
            items += [file]

        moviemenu = menu.Menu(self.name, items, umount_all = 1, xml_file=self.xml_file)

        if pop:
            pop.destroy()

        self.menuw.pushmenu(moviemenu)
        return


    def settings(self, arg=None, menuw=None):
        if not self.menuw:
            self.menuw = menuw
        pop = None
        if not self.scanned:
            self.scanned = TRUE
            
            # Use the uid to make a user-unique filename
            uid = os.getuid()

            if self.media:
                pop = PopupBox(text='Scanning disc, be patient...',
                               icon='skins/icons/misc/cdrom_mount.png')
                if not (self.mode == 'dvd' or self.mode == 'vcd'):
                    util.mount(os.path.dirname(self.filename))
            else:
                pop = PopupBox(text='Scanning file, be patient...')
    
            pop.show()

            os.system('rm -f /tmp/mplayer_dvd_%s.log /tmp/mplayer_dvd_done_%s' % (uid, uid))

            file = self.filename

            if not file:
                file = '1'

            cmd = config.MPLAYER_CMD + ' -v -nocache -nolirc -vo null -frames 0 '
            if self.media:
                cmd += ' -cdrom-device %s -dvd-device %s' % \
                       (self.media.devicename, self.media.devicename)
            if self.mode == 'dvd' or self.mode == 'vcd':
                cmd += ' -%s %s' % (self.mode, file)
            else:
                cmd += ' "%s"' % file

            cmd += ' 2> /dev/null > /tmp/mplayer_dvd_%s.log' % uid

            os.system(cmd + (' ; touch /tmp/mplayer_dvd_done_%s' % uid))

            timeout = time.time() + 20.0
            done = 0
            while 1:
                if time.time() >= timeout:
                    print 'DVD/VCD disc read failed!'
                    break

                if os.path.isfile('/tmp/mplayer_dvd_done_%s' % uid):
                    done = 1
                    break

            p = mplayer.MPlayerParser(self)
            for line in open('/tmp/mplayer_dvd_%s.log' % uid).readlines():
                p.parse(line)

            
        confmenu = configure.get_main_menu(self, self.menuw, self.xml_file)
        if pop:
            pop.destroy()
        self.menuw.pushmenu(confmenu)
        

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for this item
        """

        # when called from mplayer.py, there is no menuw
        if not menuw:
            menuw = self.menuw

        # DVD protected
        if event == rc.DVD_PROTECTED:
            AlertBox(text='The DVD is protected, see the docs for more info!').show()
            event = rc.PLAY_END

        # PLAY_END: do have have to play another file?
        if self.subitems:
            if event == rc.PLAY_END:
                try:
                    pos = self.subitems.index(self.current_subitem)
                    if pos < len(self.subitems)-1:
                        self.current_subitem = self.subitems[pos+1]
                        print "playing next item"
                        self.current_subitem.play(menuw=menuw)
                        return TRUE
                except:
                    pass
            elif event == rc.USER_END:
                pass

        # show configure menu
        if event == rc.MENU:
            self.video_player.stop()
            self.settings(menuw=menuw)
            menuw.show()
            return TRUE
        
        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
