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
            
        self.name    = os.path.splitext(os.path.basename(file))[0]
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

        

    # ------------------------------------------------------------------------
    # help function


    # Generate special menu for DVD/VCD/SVCD content
    #
    def dvd_vcd_handler(self, menuw):

        # Use the uid to make a user-unique filename
        uid = os.getuid()

        # Figure out the number of titles on this disc
        skin.PopupBox('Scanning disc, be patient...', icon='icons/cdrom_mount.png')
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
                    num_titles = int(line.split()[2])
                    print 'Got num_titles = %s from str "%s"' % (num_titles, line)
                    found = 1
                    break

        elif done:
            # Look for 'track NN'
            lines = open('/tmp/mplayer_dvd_%s.log' % uid).readlines()
            for line in lines:
                if line.find('track ') == 0:
                    num_titles = int(line[6:8])
                    found = 1

            # Count the files on the VCD
            util.mount(self.media.mountdir)
            for dirname in ('/mpegav/', '/MPEG2/', '/mpeg2/'):
                num_files += len(util.match_files(self.media.mountdir + dirname,
                                                  [ 'mpg', 'dat' ]))
            util.umount(self.media.mountdir)

        if not done or not found:
            num_titles = 100 # XXX Kludge

        #
        # Done scanning the disc, set up the menu.
        #

        self.mplayer_options += ' -cdrom-device %s -dvd-device %s' % \
                                (self.media.devicename, self.media.devicename)

        # Now let's see what we can do now:
        # only one track, play it
        if num_titles == 1:
            file = copy.copy(self)
            file.files = ('1', )
            file.play(menuw = menuw)
            return

        # build a menu
        items = []
        for title in range(1,num_titles+1):
            file = copy.copy(self)
            file.files = ('%s' % title, )
            file.name = 'Play Title %s' % (title - 1)
            items += [file]

        moviemenu = menu.Menu(self.name, items, umount_all = 1)
        menuw.pushmenu(moviemenu)

        return



    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        return [ ( self.play, 'Play' ) ]
    

    def play(self, menuw=None):
        self.parent.current_item = self
        if not self.files[0] and (self.mode == 'dvd' or self.mode == 'vcd'):
            self.dvd_vcd_handler(menuw)
        else:
            print "now playing %s" % self.files
            self.current_file = self.files[0]
            mplayer_options = self.mplayer_options

            if self.media:
                mplayer_options += '-cdrom-device %s -dvd-device %s' % \
                                   (self.media.devicename, self.media.devicename)

            self.video_player.play(self.current_file, mplayer_options, self)


    def stop(self, menuw=None):
        self.video_player.stop()


    def eventhandler(self, event, menuw=None):

        # PLAY_END: do have have to play another file?
        if event == rc.PLAY_END:
            pos = self.files.index(self.current_file)
            if pos < len(self.files)-1:
                self.current_file = self.files[pos+1]
                print "playing next file"
                self.video_player.play(self.current_file, self.mplayer_options, self)
                return TRUE

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
