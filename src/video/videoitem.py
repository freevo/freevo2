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
# Revision 1.16  2003/02/24 04:21:40  krister
# Mathieu Weber's bugfix for multipart movies
#
# Revision 1.15  2003/02/17 18:32:24  dischi
# Added the infos from the xml file to VideoItem
#
# Revision 1.14  2003/02/15 04:03:03  krister
# Joakim Berglunds patch for finding music/movie cover pics.
#
# Revision 1.13  2003/02/12 10:28:28  dischi
# Added new xml file support. The old xml files won't work, you need to
# convert them.
#
# Revision 1.12  2003/02/11 18:40:09  dischi
# Fixed bug when the title list wasn't allowed in the item menu
#
# Revision 1.11  2003/01/28 11:34:28  dischi
# Reversed the bugfix in identifymedia and fixed it in videoitem. Track 1
# should play track 1, track 0 should be dvdnav (in the future, right now
# it's also track 1).
#
# Revision 1.10  2003/01/12 10:58:31  dischi
# Changed the multiple file handling. If a videoitem has more than one file,
# the videoitem gets the filename '' and subitems for each file. With that
# change it is possible to spit a movie that part one is a VCD, part two a
# file on the harddisc.
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

rc         = rc.get_singleton()

if not config.NEW_SKIN:
    import skin
    import osd
    skin = skin.get_singleton()
    osd  = osd.get_singleton()


from gui.PopupBox import PopupBox
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

        self.subtitle_file = {}         # text subtitles
        self.audio_file = {}            # audio dubbing

        self.filename = filename
        self.name    = util.getname(filename)

        # find image for tv show and build new title
        if config.TV_SHOW_REGEXP_MATCH(self.name):
            show_name = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(self.name))
            self.name = show_name[0] + " " + show_name[1] + "x" + show_name[2] +\
                         " - " + show_name[3] 

            if os.path.isfile((config.TV_SHOW_IMAGES + show_name[0] + ".png").lower()):
                self.image = (config.TV_SHOW_IMAGES + show_name[0] + ".png").lower()
            elif os.path.isfile((config.TV_SHOW_IMAGES + show_name[0] + ".jpg").lower()):
                self.image = (config.TV_SHOW_IMAGES + show_name[0] + ".jpg").lower()

        # find image for this file
        # First check in COVER_DIR
        if os.path.isfile(config.COVER_DIR+self.name+'.png'):
            self.image = config.COVER_DIR+self.name+'.png'
        elif os.path.isfile(config.COVER_DIR+self.name+'.jpg'):
            self.image = config.COVER_DIR+self.name+'.jpg'
        # Then check for episode in TV_SHOW_IMAGES
        if os.path.isfile(os.path.splitext(filename)[0] + ".png"):
            self.image = os.path.splitext(filename)[0] + ".png"
        elif os.path.isfile(os.path.splitext(filename)[0] + ".jpg"):
            self.image = os.path.splitext(filename)[0] + ".jpg"


        self.video_player = mplayer.get_singleton()

        # variables only for VideoItem
        self.label = ''
        
        self.available_audio_tracks = []
        self.available_subtitles    = []
        self.available_chapters     = 0

        self.selected_subtitle = None
        self.selected_audio    = None
        self.num_titles        = 0
        self.deinterlace       = 0

        # XML file infos
        # possible values are: genre, runtime, tagline, plot, year, rating
        self.info = {}

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
                items += [( self.play, 'Play %s' % (m.filename))]
                if os.path.exists(util.get_bookmarkfile(m.filename)):
                    myfilename = util.get_bookmarkfile(m.filename)
                    self.current_subitem = myfilename
                    items += [( self.bookmark_menu, 'Bookmark list %s' % (myfilename))]
        return items


    def show_variants(self, arg=None, menuw=None):
        m = menu.Menu(self.name, self.variants, reload_func=None)
        menuw.pushmenu(m)

    def play(self, arg=None, menuw=None):
        """
        play the item.
        """
        self.parent.current_item = self
        
        self.menuw = menuw
        self.menuw_visible = menuw.visible

        if self.subitems:
            self.current_subitem = self.subitems[0]
            self.current_subitem.play(arg, menuw)
            return

        file = self.filename
        if self.mode == "file":
            if self.media_id:
                mountdir, file = util.resolve_media_mountdir(self.media_id,file)
                if mountdir:
                    util.mount(mountdir)
                else:
                    # TODO: prompt for the right media
                    if not config.NEW_SKIN:
                        skin.PopupBox('Media not found for file %s' % (file))
                        time.sleep(2.0)
                        rc.post_event(rc.PLAY_END)
                        menuw.refresh()
                    return
        elif self.mode == 'dvd' or self.mode == 'vcd':
            if not self.media:
                media = util.check_media(self.media_id)
                if media:
                    self.media = media
                else:
                    if not config.NEW_SKIN:
                        skin.PopupBox('Media not found for %s track %s' % (self.mode, file))
                        time.sleep(2.0)
                        rc.post_event(rc.PLAY_END)
                        menuw.refresh()
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

        if self.selected_subtitle:
            mplayer_options += ' -sid %s' % self.selected_subtitle

        if self.selected_audio:
            mplayer_options += ' -aid %s' % self.selected_audio

        if self.subtitle_file:
            d, f = util.resolve_media_mountdir(self.subtitle_file['media-id'],self.subtitle_file['file'])
            if d:
                util.mount(d)
            mplayer_options += ' -sub %s' % f

        if self.audio_file:
            d, f = util.resolve_media_mountdir(self.audio_file['media-id'],self.audio_file['file'])
            if d:
                util.mount(d)
            mplayer_options += ' -audiofile %s' % f

        if arg:
            mplayer_options += ' %s' % arg

        if self.deinterlace:
            mplayer_options += ' -vop pp=fd'


        if menuw.visible:
            menuw.hide()
        self.video_player.play(file, mplayer_options, self)


    def stop(self, arg=None, menuw=None):
        """
        stop playing
        """
        self.video_player.stop()
        if self.menuw_visible:
            menuw.show()


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

        self.menuw = menuw
        self.menuw_visible = menuw.visible

        if menuw.visible:
            menuw.hide()
        self.video_player.play('', mplayer_options, self, 'dvdnav')

    def bookmark_menu(self,arg=None, menuw=None):
        """
        Bookmark list
        """
        bookmarkfile = self.current_subitem
        items = []
        m = open(bookmarkfile,'r')
        lines = open(bookmarkfile,'r').readlines()
        for line in lines: 
            file = copy.copy(self)
            sec = int(line)
            hour = int(sec/3600)
            min = int(sec/60)
            sec = int(sec%60)
            file.filename = '%0.2d:%0.2d:%0.2d' % (hour,min,sec)
            file.name = 'Jump to %s' % (file.filename)
            file.mplayer_options += " -ss %s" % (file.filename)
            items += [file]
        
        moviemenu = menu.Menu(self.name, items)
        menuw.pushmenu(moviemenu)

        return





    def dvd_vcd_title_menu(self, arg=None, menuw=None):
        """
        Generate special menu for DVD/VCD/SVCD content
        """
        pop = None

        if not self.num_titles:
            # Use the uid to make a user-unique filename
            uid = os.getuid()

            # Figure out the number of titles on this disc
            if not config.NEW_SKIN:
                skin.PopupBox('Scanning disc, be patient...',
                              icon='skins/icons/misc/cdrom_mount.png')
                osd.update()
            else:
                pop = PopupBox('Scanning disc, be patient...',
                               icon='skins/icons/misc/cdrom_mount.png')
                menuw.add_child(pop)
                pop.osd.focused_app = pop
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

        if pop and config.NEW_SKIN:
            pop.destroy()

        #
        # Done scanning the disc, set up the menu.
        #

        # only one track, play it
        if self.num_titles == 1:
            file = copy.copy(self)
            file.filename = '1'
            file.play(menuw = menuw)
            return

        # build a menu
        items = []
        for title in range(1,self.num_titles+1):
            file = copy.copy(self)
            file.filename = '%s' % title
            file.name = 'Play Title %s' % title
            items += [file]

        moviemenu = menu.Menu(self.name, items, umount_all = 1)
        menuw.pushmenu(moviemenu)

        return


    def settings(self, arg=None, menuw=None):
        if (self.mode == 'dvd' or self.mode == 'vcd') and not self.available_audio_tracks:
            
            # Use the uid to make a user-unique filename
            uid = os.getuid()

            if not config.NEW_SKIN:
                skin.PopupBox('Scanning disc, be patient...',
                              icon='skins/icons/misc/cdrom_mount.png')
                osd.update()
            else:
                pop = PopupBox('Scanning disc, be patient...',
                               icon='skins/icons/misc/cdrom_mount.png')
                menuw.add_child(pop)
                pop.osd.focused_app = pop
                pop.show()


                
            os.system('rm -f /tmp/mplayer_dvd_%s.log /tmp/mplayer_dvd_done_%s' % (uid, uid))

            file = self.filename
            if not file:
                file = '1'

            cmd = config.MPLAYER_CMD + ' -v -nocache -nolirc -vo null -frames 0 '
            cmd += ' -cdrom-device %s -dvd-device %s' % \
                   (self.media.devicename, self.media.devicename)
            cmd += ' -%s %s 2> /dev/null > /tmp/mplayer_dvd_%s.log' % \
                   (self.mode, file, uid)

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

            if config.NEW_SKIN:
                pop.destroy()

            
        configure.main_menu(self, menuw)
        

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for this item
        """

        # when called from mplayer.py, there is no menuw
        if not menuw:
            menuw = self.menuw

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

        if event in ( rc.STOP, rc.SELECT, rc.EXIT, rc.PLAY_END, rc.USER_END ) and \
           self.menuw_visible:
            menuw.show()
            return TRUE
        
        # show configure menu
        if event == rc.MENU:
            self.video_player.stop()
            self.settings(menuw=menuw)
            menuw.show()
            return TRUE
        
        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
