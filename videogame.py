# ----------------------------------------------------------------------
# VideoGame.py - the Freevo VideoGame module
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

# The mame class
import mame

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

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

# Create the mame object
mame = mame.get_singleton()

# remember the position of the selected item in the main menu
main_menu_selected = -1

#
# mame dummy
#
def play_mame( arg=None, menuw=None ):
    mode = arg[0]
    filename = arg[1]
    playlist = arg[2]
    mame_options = ""
    if len(arg) > 3:
        mame_options = arg[3]

    # Check if the file is on a drive that needs to be mounted
    for media in config.REMOVABLE_MEDIA:
        if string.find(filename, media.mountdir) == 0:
            util.mount(media.mountdir)
            
    ## Change we dont use playlists ##            
    mame.play(mode, filename, playlist, 0, mame_options)


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

    for (title, dir) in config.DIR_MAME:
        items += [menu.MenuItem(title, cwd, dir, eventhandler, type = 'dir')]

    for media in config.REMOVABLE_MEDIA:
        if media.info:
            # Is this media playable as is?
            if media.info.play_options:
                m = menu.MenuItem(media.info.label, play_mame, media.info.play_options,
                                  eventhandler, media)
            elif type != None:
                # Just data files
                m = menu.MenuItem('Drive ' + media.drivename, cwd, dir,
                                  eventhandler, media)
            m.setImage(('movie', media.info.image))
        else:
            m = menu.MenuItem('Drive %s (no disc)' % media.drivename, None,
                              None, eventhandler, media)
        items += [m]

    return items


def main_menu(arg=None, menuw=None):

    # Check for the 'rominfo' helper app first, it is required!
    if not os.path.isfile('./rominfo'):
        osd.popup_box('The "rominfo" program was not found!')
        osd.update()
        time.sleep(2)
        rc.post_event(rc.REFRESH_SCREEN)
        return
    
    mamemenu = menu.Menu('VIDEOGAME MAIN MENU', main_menu_generate(), umount_all=1)
    menuw.pushmenu(mamemenu)



#
# The change directory handling function
#
def cwd(arg=None, menuw=None):
    mamedir = arg

    for media in config.REMOVABLE_MEDIA:
        if media.mountdir == mamedir:
            util.mount(mamedir)
                
    dirnames = util.getdirnames(mamedir)
    mame_files = util.match_files(mamedir, config.SUFFIX_MAME_FILES)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
        m = menu.MenuItem(title, cwd, dirname, type = 'dir', eventhandler = eventhandler)

        items += [m]

    files = []

    # Mame files
    for file in mame_files:
        title = os.path.splitext(os.path.basename(file))[0]
        image = None
        rominfo = os.popen('./rominfo ' + file , 'r')
        matched = 0
	partial = 0
	for line in rominfo.readlines():
            if string.find(line, 'Error:') != -1:
                print 'MAME:rominfosrc: "%s"' % line.strip()
            if string.find(line, 'KNOWN:') != -1:
                print 'MAME:rominfosrc: "%s"' % line.strip()
                matched = 1
            if string.find(line, 'PARTIAL:') != -1:
                print 'MAME:rominfosrc: "%s"' % line.strip()
                partial = 1
        rominfo.close()
	if matched == 1 or partial == 1:
            # find image for this file
            if os.path.isfile(os.path.splitext(file)[0] + ".png"):
                image = os.path.splitext(file)[0] + ".png"
            elif os.path.isfile(os.path.splitext(file)[0] + ".jpg"):
                image = os.path.splitext(file)[0] + ".jpg"

            # add file to list
            files += [ ( title, 'mame', file, [], None, image ) ]


    # sort files by title
    files.sort(lambda l, o: cmp(l[0].upper(), o[0].upper()))

    # add everything to the menu
    # AGAIN WE ARE NOT USING PLAYLISTS
    for (title, mode, file, playlist, mame_options, image) in files:
        m = menu.MenuItem(title, play_mame, (mode, file, playlist, mame_options),
                          eventhandler = eventhandler)
        m.setImage(('movie', image))
        items += [m]
    
    mamemenu = menu.Menu('VIDEOGAME MENU', items, xml_file=mamedir)

    if len(menuw.menustack) > 1:
        if menuw.menustack[1] == menuw.menustack[-1]:
            global main_menu_selected
            main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)
        
    menuw.pushmenu(mamemenu)
