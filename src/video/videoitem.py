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
# Revision 1.6  2002/12/12 11:45:02  dischi
# Moved all icons to skins/icons
#
# Revision 1.5  2002/12/03 20:03:43  dischi
# Now it's impossible to show the dvd title menu when you are already in this
# menu. Also dvdnav support is now working (more or less, depends if mplayer
# can dvdnav your dvd). Give it a try and select dvdnav in the item menu
#
# Revision 1.4  2002/12/03 19:16:23  dischi
# Some changes in actions(): play will always play the item, for DVD/VCD
# this means track 1. The DVD/VCD title menu is an extra action
#
# Revision 1.3  2002/11/28 19:56:12  dischi
# Added copy function
#
# Revision 1.2  2002/11/26 20:58:44  dischi
# o Fixed bug that not only the first character of mplayer_options is used
# o added the configure stuff again (without play from stopped position
#   because the mplayer -ss option is _very_ broken)
# o Various fixes in DVD playpack
#
# Revision 1.1  2002/11/24 13:58:45  dischi
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
import re

import config
import util
import mplayer

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

import menu
import rc
import skin
import osd
import time
import copy

rc         = rc.get_singleton()
skin       = skin.get_singleton()
osd        = osd.get_singleton()

from item import Item
import configure


class VideoItem(Item):
    def __init__(self, files, parent):
        Item.__init__(self, parent)

        # fix values
        self.type  = 'video'
        self.handle_type = 'video'

        self.mode  = 'file'             # file, dvd or vcd

        # files can be a list of files, one file or nothing (e.g. dvd)
        if not files:
            file = ''
            self.files = [ file, ]
        elif isinstance(files, list):
            file = files[0]
            self.files = files
        else:
            file = files
            self.files = [ file, ]
            
        self.name    = util.getname(file)
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
        if os.path.isfile(os.path.splitext(file)[0] + ".png"):
            self.image = os.path.splitext(file)[0] + ".png"
        elif os.path.isfile(os.path.splitext(file)[0] + ".jpg"):
            self.image = os.path.splitext(file)[0] + ".jpg"


        self.video_player = mplayer.get_singleton()

        # variables only for VideoItem
        self.available_audio_tracks = []
        self.available_subtitles    = []
        self.available_chapters     = 0

        self.selected_subtitle = None
        self.selected_audio    = None
        self.num_titles        = 0


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



    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        items = [ (self.play, 'Play') ]

        # show DVD/VCD title menu for DVDs, but only when we aren't in a
        # submenu of a such a menu already
        if not self.files[0]:
            if self.mode == 'dvd':
                items += [( self.dvdnav, 'DVD Menu (experimental)' )]
                items += [( self.dvd_vcd_title_menu, 'DVD title list' )]
            if self.mode == 'vcd':
                items += [( self.dvd_vcd_title_menu, 'VCD title list' )]
        return items


    def play(self, arg=None, menuw=None):
        """
        play the item.
        """
        self.parent.current_item = self
        self.current_file = self.files[0]

        if not self.files[0] and (self.mode == 'dvd' or self.mode == 'vcd'):
            self.current_file = '1'

        mplayer_options = self.mplayer_options

        if self.media:
            mplayer_options += ' -cdrom-device %s -dvd-device %s' % \
                               (self.media.devicename, self.media.devicename)

        if self.selected_subtitle:
            mplayer_options += ' -sid %s' % self.selected_subtitle

        if self.selected_audio:
            mplayer_options += ' -aid %s' % self.selected_audio

        if arg:
            mplayer_options += ' %s' % arg

        self.video_player.play(self.current_file, mplayer_options, self)


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

        self.video_player.play('', mplayer_options, self, 'dvdnav')



    def dvd_vcd_title_menu(self, arg=None, menuw=None):
        """
        Generate special menu for DVD/VCD/SVCD content
        """
        if not self.num_titles:
            # Use the uid to make a user-unique filename
            uid = os.getuid()

            # Figure out the number of titles on this disc
            skin.PopupBox('Scanning disc, be patient...',
                          icon='skins/icons/misc/cdrom_mount.png')
            osd.update()
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

        #
        # Done scanning the disc, set up the menu.
        #

        # only one track, play it
        if self.num_titles == 1:
            file = copy.copy(self)
            file.files = [ '1', ]
            file.play(menuw = menuw)
            return

        # build a menu
        items = []
        for title in range(1,self.num_titles+1):
            file = copy.copy(self)
            file.files = ['%s' % title, ]
            file.name = 'Play Title %s' % title
            items += [file]

        moviemenu = menu.Menu(self.name, items, umount_all = 1)
        menuw.pushmenu(moviemenu)

        return


    def eventhandler(self, event, menuw=None):
        """
        eventhandler for this item
        """
        
        # PLAY_END: do have have to play another file?
        if event == rc.PLAY_END:
            try:
                pos = self.files.index(self.current_file)
                if pos < len(self.files)-1:
                    self.current_file = self.files[pos+1]
                    print "playing next file"
                    self.video_player.play(self.current_file, self.mplayer_options, self)
                    return TRUE
            except:
                pass

        # show configure menu
        if event == rc.MENU:
            self.video_player.stop()
            configure.main_menu(self)
            
        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
