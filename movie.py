# ----------------------------------------------------------------------
# movie.py - the Freevo Movie module
# ----------------------------------------------------------------------
# $Id$
#
# Authors:     Krister Lagerstrom <krister@kmlager.com>
#              Aubin Paul <aubin@punknews.org>
#              Dirk Meyer <dischi@tzi.de>
# Notes:
# Todo:        
#
# ----------------------------------------------------------------------
# $Log$
# Revision 1.40  2002/09/22 18:14:57  dischi
# Renamed dvd_vcd_menu_generate to dvd_vcd_handler with more
# intelligence: count the number of mpg files _and_ the number of
# tracks. If there is only on track, build no menu and play the
# track. If there are two tracks and only one file, than the first track
# is the VCD menu, action is play track 2. If there is one track more
# than files, don't show track one in the menu, it's the VCD menu.
#
# Revision 1.39  2002/09/21 10:12:11  dischi
# Moved osd.popup_box to skin.PopupBox. A popup box should be part of the
# skin.
#
# Revision 1.38  2002/09/19 19:10:18  dischi
# bugfix
#
# Revision 1.37  2002/09/18 18:42:19  dischi
# Some small changes here and there, nothing important
#
# Revision 1.36  2002/09/15 12:44:31  dischi
# skin support for DVD/VCD/SVCD was missing
#
# Revision 1.35  2002/09/15 12:32:01  dischi
# The DVD/VCD/SCVD/CD description file for the automounter can now also
# contain skin informations. An announcement will follow. For this the
# paramter dir in menu.py is renamed to xml_file since the only use
# was to find the xml file. All other modules are adapted (dir -> xml_file)
#
# Revision 1.34  2002/09/15 11:53:41  dischi
# Make info in RemovableMedia a class (RemovableMediaInfo)
#
# Revision 1.33  2002/09/13 17:34:59  dischi
# Added menu with all tracks for (S)VCDs. Currently I only have one SVCD
# for testing, but it should work for VCDs, too. We need a way to check
# if track 1 is playable or not (menu)
#
# Revision 1.32  2002/09/13 16:30:45  dischi
# Fix DVD title scanning, added -cdrom-device for title search and DVD play,
# menu title is DVD title, added DVD image for all items
#
# Revision 1.31  2002/09/13 08:01:23  dischi
# fix -cdrom-device for (S)VCD
#
# Revision 1.30  2002/09/12 08:36:59  dischi
# Show identified title instead of the disc label for non
# right-now-playable discs.
#
# Revision 1.25  2002/09/04 19:32:31  dischi
# Added a new identifymedia. Freevo now polls the rom drives for media
# change and won't mount the drive unless you want to play a file from cd or
# you browse it.
#
#
# ----------------------------------------------------------------------
# 
# Copyright (C) 2002 Krister Lagerstrom
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
# ----------------------------------------------------------------------
#


import sys
import random
import time, os, string

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The menu widget class
import menu

# The mplayer class
import mplayer

# XML support
import movie_xml

# RegExp
import re

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# Create the remote control object
rc = rc.get_singleton()

# Create the OSD object
osd = osd.get_singleton()

import skin    # The skin class
skin = skin.get_singleton()

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

# Create the mplayer object
mplayer = mplayer.get_singleton()

# remember the position of the selected item in the main menu
main_menu_selected = -1

#
# mplayer dummy
#
def play_movie(arg=None, menuw=None):
    mode = arg[0]      # 'dvd', 'vcd', etc
    filename = arg[1]
    playlist = arg[2]
    play_options = ""

    if len(arg) > 3:
        play_options = arg[3]
        
    print 'playmovie: Got arg=%s, filename="%s"' % (arg, filename)

    # Is the file on a removable media? If so it needs to be mounted.
    for media in config.REMOVABLE_MEDIA:
        if filename.find(media.mountdir) == 0:
            if mode == 'dvd':
                dvd_vcd_handler(media, 'dvd', menuw)
                return
            if mode == 'vcd' or mode == 'svcd':
                dvd_vcd_handler(media, 'vcd', menuw)
                return
            else:
                util.mount(media.mountdir)
                break
                
    mplayer.play(mode, filename, playlist, 0, play_options)


def play_dvd(arg=None, menuw=None):
    titlenum = arg
    print 'play_dvd: Got title %s' % titlenum
    mplayer.play('dvd', titlenum, [], 0, '')

def play_vcd(arg=None, menuw=None):
    titlenum = arg
    print 'play_vcd: Got title %s' % titlenum
    mplayer.play('vcd', titlenum, [], 0, '')


#
# Generate special menu for DVD/VCD/SVCD content
#
def dvd_vcd_handler(media, type, menuw):

    # Figure out the number of titles on this disc
    skin.PopupBox('Scanning disc, be patient...', icon='icons/cdrom_mount.png')
    osd.update()
    os.system('rm /tmp/mplayer_dvd.log /tmp/mplayer_dvd_done')

    cmd = ('%s -ao null -nolirc -vo null -frames 0 %s -cdrom-device %s ' +
           '2>&1 > /tmp/mplayer_dvd.log')

    if type == 'dvd':
        #mplayer -ao null -nolirc -vo null -frames 0 -dvd 1 2> &1 > /tmp/mplayer_dvd.log
        cmd = cmd % (config.MPLAYER_CMD, '-dvd 1', media.devicename)
        play_function = play_dvd
    else:
        # play track 99 which isn't there (very sure!), scan mplayers list
        # of found tracks to get the total number of tracks
        #mplayer -ao null -nolirc -vo null -frames 0 -vcd 99 2> &1 > /tmp/mplayer_dvd.log
        cmd = cmd % (config.MPLAYER_CMD, '-vcd 99', media.devicename)
        play_function = play_vcd

    os.system(cmd + ' ; touch /tmp/mplayer_dvd_done')

    timeout = time.time() + 20.0
    done = 0
    while 1:
        if time.time() >= timeout:
            print 'DVD/VCD disc read failed!'
            break

        if os.path.isfile('/tmp/mplayer_dvd_done'):
            done = 1
            break

    found = 0
    num_files = 0

    if done and type == 'dvd':
        # Look for 'There are NNN titles on this DVD'
        lines = open('/tmp/mplayer_dvd.log').readlines()
        for line in lines:
            if line.find('titles on this DVD') != -1:
                num_titles = int(line.split()[2])
                print 'Got num_titles = %s from str "%s"' % (num_titles, line)
                found = 1
                break

    elif done:
        # Look for 'track NN'
        lines = open('/tmp/mplayer_dvd.log').readlines()
        for line in lines:
            if line.find('track ') == 0:
                num_titles = int(line[6:8])
                found = 1

        # Count the files on the VCD
        util.mount(media.mountdir)
        for dir in ('/mpegav/', '/MPEG2/', '/mpeg2/'):
            num_files += len(util.match_files(media.mountdir + dir,
                                              [ '*.[mM][pP][gG]',
                                                '*.[dD][aA][tT]' ]))
        util.umount(media.mountdir)
        
    if not done or not found:
        num_titles = 100 # XXX Kludge

    # Now let's see what we can do now:
    
    # only one track, play it
    if num_titles == 1:
        play_function('1 -cdrom-device %s' % media.devicename)
        return
    
    # two tracks and only one file, play 2
    if num_titles == 2 and num_files == 1:
        play_function('2 -cdrom-device %s' % media.devicename)
        return
    
    # one track more than files, track 1 is menu, ignore it
    # mplayer can play some menus by playing all tracks, but IMHO it's
    # better not to show the disc menu here as playable track
    if num_titles == num_files + 1:
        items = []
        for title in range(2,num_titles+1):
            m = menu.MenuItem('Play Title %s' % (title - 1), play_function,
                              '%s -cdrom-device %s' % (title, media.devicename), 
                              dvd_menu_eventhandler, media)
            m.setImage(('movie', media.info.image))
            items += [m]

        label = media.info.label
        moviemenu = menu.Menu(label, items, xml_file = media.info.xml_file, umount_all = 1)
        menuw.pushmenu(moviemenu)
        return
    
    # build a normal menu
    items = []
    for title in range(1,num_titles+1):
        m = menu.MenuItem('Play Title %s' % title, play_function,
                          '%s -cdrom-device %s' % (title, media.devicename), 
                          dvd_menu_eventhandler, media)
        m.setImage(('movie', media.info.image))
        items += [m]

    label = media.info.label
    moviemenu = menu.Menu(label, items, xml_file = media.info.xml_file, umount_all = 1)
    menuw.pushmenu(moviemenu)

    return


#
# EJECT handling for when we're in the DVD title menu.
#
def dvd_menu_eventhandler(event = None, menuw=None, arg=None):

    if event == rc.EJECT:
        print 'EJECT: Arg=%s' % arg

        menuw.back_one_menu()
        menuw.refresh()

        if not arg: return

        media = arg
        media.move_tray(dir='toggle')
        

#
# EJECT handling
#
def eventhandler(event = None, menuw=None, arg=None):

    global main_menu_selected
    if event == rc.IDENTIFY_MEDIA:
        if menuw.menustack[1] == menuw.menustack[-1]:
            main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)

        menuw.menustack[1].choices = main_menu_generate()

        menuw.menustack[1].selected = menuw.menustack[1].choices[main_menu_selected]

        if menuw.menustack[1] == menuw.menustack[-1]:
            menuw.init_page()
            menuw.refresh()

    if event == rc.EJECT:

        print 'EJECT1: Arg=%s' % arg

        # Was the handler called for a specific drive?
        if not arg:
            print 'Arg was none'
            if not config.REMOVABLE_MEDIA:
                print 'No removable media defined'
                return # Do nothing if no media defined
            # Otherwise open/close the first drive in the list
            media = config.REMOVABLE_MEDIA[0]
            print 'Selecting first device'
        else:
            media = arg

        print media    
        print dir(media)
        media.move_tray(dir='toggle')

    # Done
    return


# ======================================================================


#
# The Movie module main menu
#
def main_menu_generate():
    items = []

    for (title, dir) in config.DIR_MOVIES:
        items += [menu.MenuItem(title, cwd, dir, eventhandler, type = 'dir')]

    for media in config.REMOVABLE_MEDIA:
        if media.info:

            # Right now we only display the title if we have one and
            # the title contains the name of the drive for unknown
            # discs. Should we display more infos even on known discs?

            # a) the label like it is
            # b) Drive x: label
            # c) Drive x: type label

            # Is this media playable as is?
            if media.info.play_options:
                m = menu.MenuItem(media.info.label, play_movie, media.info.play_options,
                                  eventhandler, media)

            elif media.info.type != None:
                # Just data files
                m = menu.MenuItem(media.info.label, cwd, media.mountdir, eventhandler, media)
            m.setImage(('movie', media.info.image))
        else:
            m = menu.MenuItem('Drive %s (no disc)' % media.drivename, None,
                              None, eventhandler, media)
        items += [m]

    return items


def main_menu(arg=None, menuw=None):
    moviemenu = menu.Menu('MOVIE MAIN MENU', main_menu_generate(), umount_all=1)
    menuw.pushmenu(moviemenu)



#
# The change directory handling function
#
def cwd(arg=None, menuw=None):
    mountdir = arg
    skin_xml_file = mountdir
    
    for media in config.REMOVABLE_MEDIA:
        if string.find(mountdir, media.mountdir) == 0:
            util.mount(mountdir)
            if media.info and media.info.xml_file:
                skin_xml_file = media.info.xml_file
                
    dirnames = util.getdirnames(mountdir)
    mplayer_files = util.match_files(mountdir, config.SUFFIX_MPLAYER_FILES)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
        m = menu.MenuItem(title, cwd, dirname, type = 'dir', eventhandler = eventhandler)
        if os.path.isfile(dirname+'/cover.png'): 
            m.setImage(('movie', (dirname+'/cover.png')))
        if os.path.isfile(dirname+'/cover.jpg'): 
            m.setImage(('movie', (dirname+'/cover.jpg')))

        items += [m]
    
    files = []

    # XML files
    for file in util.match_files(mountdir, config.SUFFIX_FREEVO_FILES):
        title, image, (mode, first_file, playlist, play_options), id, label, info =\
               movie_xml.parse(file, mountdir, mplayer_files)

        # only add movies when we have all needed informations
        if title != "" and first_file != "":
            files += [ ( title, mode, first_file, playlist, play_options, image ) ]

    # "normal" movie files
    for file in mplayer_files:
        title = os.path.splitext(os.path.basename(file))[0]
        image = None

        # find image for tv show and build new title
        if config.TV_SHOW_REGEXP_MATCH(title):
            show_name = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(title))
            title = show_name[0] + " " + show_name[1] + "x" + show_name[2] + " - " + \
                    show_name[3] 

            if os.path.isfile((config.TV_SHOW_IMAGES + show_name[0] + ".png").lower()):
                image = (config.TV_SHOW_IMAGES + show_name[0] + ".png").lower()
            elif os.path.isfile((config.TV_SHOW_IMAGES + show_name[0] + ".jpg").lower()):
                image = (config.TV_SHOW_IMAGES + show_name[0] + ".jpg").lower()


        # find image for this file
        if os.path.isfile(os.path.splitext(file)[0] + ".png"):
            image = os.path.splitext(file)[0] + ".png"
        elif os.path.isfile(os.path.splitext(file)[0] + ".jpg"):
            image = os.path.splitext(file)[0] + ".jpg"

        # add file to list
        files += [ ( title, 'video', file, [], None, image ) ]


    # sort "normal" files and xml files by title
    files.sort(lambda l, o: cmp(l[0].upper(), o[0].upper()))

    # add everything to the menu
    for (title, mode, file, playlist, play_options, image) in files:
        m = menu.MenuItem(title, play_movie, (mode, file, playlist, play_options),
                          eventhandler = eventhandler)
        m.setImage(('movie', image))
        items += [m]
    
    moviemenu = menu.Menu('MOVIE MENU', items, xml_file=skin_xml_file)

    if len(menuw.menustack) > 1:
        if menuw.menustack[1] == menuw.menustack[-1]:
            global main_menu_selected
            main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)
        
    menuw.pushmenu(moviemenu)
