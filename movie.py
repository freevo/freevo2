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
# Revision 1.26  2002/09/04 19:47:46  dischi
# wrap (u)mount to get rid of the error messages
#
# Revision 1.25  2002/09/04 19:32:31  dischi
# Added a new identifymedia. Freevo now polls the rom drives for media
# change and won't mount the drive unless you want to play a file from cd or
# you browse it.
#
# Revision 1.24  2002/09/01 09:43:45  dischi
# Added type = 'dir' for directories in MenuItem so that the skin can
# use the correct style
#
# Revision 1.23  2002/08/12 12:42:17  dischi
# cosmetic changes
#
# Revision 1.22  2002/08/11 09:32:59  dischi
# If the movie title is a tv show (regexp TV_SHOW_REGEXP_MATCH) add \t
# between name, number and title for a nice alignment with the new SDL
# osd. This may cause some trouble with the krister1 skin if you have
# series and other movies in the same dir.
#
# Revision 1.21  2002/08/08 03:16:56  krister
# Changed move playing so that the next movie is not started automatically.
#
# Revision 1.20  2002/08/07 18:54:08  dischi
# changed the "mounting..." box to osd.popup_box
#
# Revision 1.19  2002/07/31 08:07:23  dischi
# Moved the XML movie file parsing in a new file. Both movie.py and
# config.py use the same code now.
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
def play_movie( arg=None, menuw=None ):
    mode = arg[0]
    filename = arg[1]
    playlist = arg[2]
    mplayer_options = ""
    if len(arg) > 3:
        mplayer_options = arg[3]

    if config.ROM_DRIVES:
        for rom in config.ROM_DRIVES:
            if string.find(filename, rom[0]) == 0:
                util.mount(rom[0])
                
    mplayer.play(mode, filename, playlist, 0, mplayer_options)


#
# EJECT handling
#
def eventhandler(event = None, menuw=None, arg=None):

    if event == rc.IDENTIFY_MEDIA:
        if menuw.menustack[1] == menuw.menustack[-1]:
            main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)

        menuw.menustack[1].choices = main_menu_generate()

        global main_menu_selected
        menuw.menustack[1].selected = menuw.menustack[1].choices[main_menu_selected]

        if menuw.menustack[1] == menuw.menustack[-1]:
            menuw.init_page()
            menuw.refresh()

            
    if event == rc.EJECT:

        rom = arg[0]
        if not rom:
            return

        # find the drive
        pos = 0
        for (dir, device, name, tray, lastcode, info) in config.ROM_DRIVES:
            if rom == dir:
                tray_open = tray
                config.ROM_DRIVES[pos] = (dir, device, name, (tray + 1) % 2, lastcode, info)
                break
            pos += 1

        if tray_open:
            if DEBUG: print 'Inserting %s' % rom
            osd.popup_box( 'mounting %s' % rom )
            osd.update()
            
            # close the tray, identifymedia does the rest
            os.system('eject -t %s' % rom)

        else:
            if DEBUG: print 'Ejecting %s' % rom
            os.system('eject %s' % rom)
        


# ======================================================================


#
# The Movie module main menu
#
def main_menu_generate():
    items = []

    for (title, dir) in config.DIR_MOVIES:
        items += [menu.MenuItem(title, cwd, dir, eventhandler, type = 'dir')]

    if config.ROM_DRIVES != None: 
        for (dir, device, name, tray, lastcode, info) in config.ROM_DRIVES:
            if info:
                (type, label, image, play_options ) = info
                if play_options:
                    m = menu.MenuItem(label, play_movie, play_options, eventhandler, (dir,))
                elif type != None:
                    m = menu.MenuItem(label, cwd, dir, eventhandler, (dir,))
                m.setImage(('movie', image))
            else:
                m = menu.MenuItem('%s (no disc)' % name, None, None, eventhandler, (dir,))
            items += [m]
            
    return items


def main_menu(arg=None, menuw=None):
    moviemenu = menu.Menu('MOVIE MAIN MENU', main_menu_generate(), umount_all = 1)
    menuw.pushmenu(moviemenu)



#
# The change directory handling function
#
def cwd(arg=None, menuw=None):
    dir = arg

    if config.ROM_DRIVES:
        for rom in config.ROM_DRIVES:
            if rom[0] == dir:
                util.mount(rom[0])
                
    dirnames = util.getdirnames(dir)
    mplayer_files = util.match_files(dir, config.SUFFIX_MPLAYER_FILES)

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
    for file in util.match_files(dir, config.SUFFIX_FREEVO_FILES):
        title, image, (mode, first_file, playlist, mplayer_options), id, info =\
               movie_xml.parse(file, dir, mplayer_files)

        # only add movies when we have all needed informations
        if title != "" and first_file != "":
            files += [ ( title, mode, first_file, playlist, mplayer_options, image ) ]

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
    for (title, mode, file, playlist, mplayer_options, image) in files:
        m = menu.MenuItem(title, play_movie, (mode, file, playlist, mplayer_options),
                          eventhandler = eventhandler)
        m.setImage(('movie', image))
        items += [m]
    
    moviemenu = menu.Menu('MOVIE MENU', items, dir=dir)

    if len(menuw.menustack) > 1:
        if menuw.menustack[1] == menuw.menustack[-1]:
            global main_menu_selected
            main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)
        
    menuw.pushmenu(moviemenu)
