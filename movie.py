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
# Revision 1.29  2002/09/08 18:26:03  krister
# Applied Andrew Drummond's MAME patch. It seems to work OK on X11, but still needs some work before it is ready for prime-time...
#
# Revision 1.28  2002/09/07 06:19:45  krister
# Improved removable media support.
#
# Revision 1.27  2002/09/06 05:25:18  krister
# Fixed a syntax warning.
#
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
def play_movie(arg=None, menuw=None):
    mode = arg[0]      # 'dvd', 'vcd', etc
    filename = arg[1]
    playlist = arg[2]
    mplayer_options = ""

    if len(arg) > 3:
        mplayer_options = arg[3]

    print 'playmovie: Got arg=%s, filename="%s"' % (arg, filename)

    # Is the file on a removable media? If so it needs to be mounted.
    for media in config.REMOVABLE_MEDIA:
        if filename.find(media.mountdir) == 0:
            if mode == 'dvd':
                dvd_menu_generate(media, menuw)
                return
            if mode == 'vcd':
                # XXX A kludge to make (S)VCD work by just playing chapter 1
                # XXX on the selected drive
                mplayer.play(mode, '1', [], 0, '-cdrom-device %s' % media.devicename)
                return
            else:
                util.mount(media.mountdir)
                break
                
    mplayer.play(mode, filename, playlist, 0, mplayer_options)


def play_dvd(arg=None, menuw=None):
    titlenum = arg

    print 'play_dvd: Got title %s' % titlenum
                
    mplayer.play('dvd', titlenum, [], 0, '')


#mplayer -ao null -nolirc -vo null -frames 0 -dvd 1 1> /dev/null 2> /tmp/mplayer_dvd.log
def dvd_menu_generate(media, menuw):

    # Figure out the number of titles on this disc
    osd.popup_box('Scanning DVD, be patient...')
    osd.update()
    os.system('rm /tmp/mplayer_dvd.log /tmp/mplayer_dvd_done')
    # XXX Add an option for DVD device to use in case theres more than one!
    cmd = ('%s -ao null -nolirc -vo null -frames 0 -dvd 1 ' +
           '1> /dev/null 2> /tmp/mplayer_dvd.log')
    os.system((cmd % config.MPLAYER_CMD) + ' ; touch /tmp/mplayer_dvd_done')
    timeout = time.time() + 20.0
    done = 0
    while 1:
        if time.time() >= timeout:
            print 'DVD disc read failed!'
            break

        if os.path.isfile('/tmp/mplayer_dvd_done'):
            done = 1
            break
    found = 0
    if done:
        # Look for 'There are NNN titles on this DVD'
        lines = open('/tmp/mplayer_dvd.log').readlines()
        for line in lines:
            if line.find('titles on this DVD') != -1:
                num_titles = int(line.split()[2])
                print 'Got num_titles = %s from str "%s"' % (num_titles, line)
                found = 1
                break

    if not done or not found:
        num_titles = 100 # XXX Kludge
    
    items = []
    for title in range(1,num_titles+1):
        m = menu.MenuItem('Play Title %s' % title, play_dvd, title,
                          dvd_menu_eventhandler, media)
        items += [m]

    label = media.info[2]
    moviemenu = menu.Menu('DVD Titles for disc %s' % label, items,
                          umount_all = 1)
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
            (type, label, image, play_options) = media.info
            # Is this media playable as is?
            if play_options:
                m = menu.MenuItem(label, play_movie, play_options,
                                  eventhandler, media)
            elif type != None:
                # Just data files
                m = menu.MenuItem('Drive ' + media.drivename, cwd, dir,
                                  eventhandler, media)
            m.setImage(('movie', image))
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

    for media in config.REMOVABLE_MEDIA:
        if media.mountdir == mountdir:
            util.mount(mountdir)
                
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
        title, image, (mode, first_file, playlist, mplayer_options), id, info =\
               movie_xml.parse(file, mountdir, mplayer_files)

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
    
    moviemenu = menu.Menu('MOVIE MENU', items, dir=mountdir)

    if len(menuw.menustack) > 1:
        if menuw.menustack[1] == menuw.menustack[-1]:
            global main_menu_selected
            main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)
        
    menuw.pushmenu(moviemenu)
