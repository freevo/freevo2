#
# imenu.py
#
# This is the Freevo image viewer menu module. 
#
# $Id$

import sys
import random
import time, os
import signal
import string, popen2, fcntl, select, struct, fnmatch
import re, sre
import rc

# Configuration file. Determines where to look for image files, etc
import config

# Various utilities
import util

# The OSD class, used to communicate with the OSD daemon
import osd

# The menu widget class
import menu

from playlist import read_playlist

# The Freevo image viewer
import iview

# The bins discriptions loader
import bins

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


osd   = osd.get_singleton()
iview = iview.get_singleton()
rc    = rc.get_singleton()

# remember the position of the selected item in the main menu
main_menu_selected = -1

# Slide show globals.
playlist_lines = []

#
# signal handler
#
def view_handler(signum, frame):
    global playlist_lines
    iview.slide_num += 1
    if iview.slide_num < iview.total_slides:
        iview.view ( playlist_lines[iview.slide_num][0], iview.slide_num, playlist_lines, 1 )
        signal.alarm ( playlist_lines[iview.slide_num][2] )


#
# view the image
#
def view_image(arg=None, menuw=None):
    osd.clearscreen(color=osd.COL_BLACK)
           
    osd.drawstring('please wait...', osd.width/2 - 60, osd.height/2 - 10,
                   fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
    osd.update()

    file = arg[0]
    number = arg[1]
    playlist = arg[2]
    mode = arg[3]
    iview.view(file, number, playlist, mode)


    
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


#
# The image viewer main menu
#
def main_menu_generate():
    items = []    

    for title, dirname in config.DIR_IMAGES:
        matched = 0
        if util.match_suffix(dirname, config.SUFFIX_IMAGE_SSHOW):
            items += [menu.MenuItem(title, slideshow, dirname, eventhandler,
                                    type = 'show')]
        else:
            items += [menu.MenuItem(title, cwd, dirname, eventhandler,
                                    type = 'dir')]

    for media in config.REMOVABLE_MEDIA:
        if media.info:

            if not media.info.label:
                print "WARNING: no title for %s given, setting to default" % media.mountdir
                media.info.label = media.mountdir
                
            if media.info.type:
                if media.info.type == 'DVD' or media.info.type == 'VCD' or \
                   media.info.type == 'SVCD':

                    m = menu.MenuItem('%s (%s)' % (media.info.label, media.info.type),
                                      None, None, eventhandler, media)
                    m.setImage(('movie', media.info.image))
                    
                else:
                    image_type = 'image'
                    label = media.info.label
                    
                    if media.info.type == 'VIDEO':
                        image_type = 'movie'
                        label += ' (Video CD)' 
                    
                    if media.info.type == 'AUDIO':
                        image_type = 'audio'
                        label += ' (Audio CD)' 
                    
                    m = menu.MenuItem(label, cwd, media.mountdir, eventhandler, media)
                    m.setImage((image_type, media.info.image))
                    
        else:
            m = menu.MenuItem('Drive %s (no disc)' % media.drivename, None,
                              None, eventhandler, media)
        items += [m]

    return items


def main_menu(arg=None, menuw=None):
    imagemenu = menu.Menu('VIEWER MAIN MENU', main_menu_generate(), umount_all=1)
    menuw.pushmenu(imagemenu)


#
# The image viewer module change directory handling function
#
def cwd(arg=None, menuw=None):
    dir = arg

    skin_xml_file=dir
    movie_info_media = None
    
    for media in config.REMOVABLE_MEDIA:
        if string.find(dir, media.mountdir) == 0:
            util.mount(dir)
            if media.info:
                movie_info_media = media.info.info

    if movie_info_media:
        skin_xml_file = movie_info_media.xml_file
                
    dirnames = util.getdirnames(dir)
    files = util.match_files(dir, config.SUFFIX_IMAGE_FILES)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
	if os.path.isfile(dirname+'/album.xml'):
	    title = '[' + bins.get_album_title(dirname) + ']'
        items += [menu.MenuItem(title, cwd, dirname, type = 'dir')]

    if len(files) > 1:
        items += [menu.MenuItem('Auto Slide Show', auto_slideshow, dir,
                                eventhandler, type = 'show')]
    
    number = 0

    for file in files:
        title = os.path.splitext(os.path.basename(file))[0]
        m = menu.MenuItem(title, view_image, (file, number, files, 0))

        m.setImage(('photo', file))

        items += [m]

        number += 1


    # if there is only one item and this item is a directory,
    # go into this directory
    #
    # XXX should make integrate this in movie/music, too?
    if len(items) == 1 and len(dirnames) == 1:
        return cwd(arg=dirnames[0], menuw=menuw)
        
    imagemenu = menu.Menu('IMAGE MENU', items, xml_file=skin_xml_file)
    menuw.pushmenu(imagemenu)

#  How to run an image slide show. 
#
#  What if we make the slideshow have a "playlist" type file and 
#  read the images and captions from that?

def slideshow(arg=None, menuw=None):
    playlist = arg

    global playlist_lines
    playlist_lines = []

    playlist_lines = read_playlist ( playlist, 0 )
    iview.total_slides = len ( playlist_lines )
    iview.slide_num = 0

    if iview.total_slides > 0:
        iview.view ( playlist_lines[0][0], 0, playlist_lines, 1 )
        # Need to check if the alarmm signal is already in use!!!
        signal.signal ( signal.SIGALRM, view_handler )
        signal.alarm ( playlist_lines[0][2] )


#  Create a slideshow from a directory of images
#
#  Dynamiclly build a playlist and start a slide show using it
#  The playlist will not contain any captions and it will use the
#  default delay value between images.

def auto_slideshow(arg=None, menuw=None):
    dirname = arg

    global playlist_lines
    playlist_lines = []

    filenames = util.match_files(dirname, config.SUFFIX_IMAGE_FILES)
    for filename in filenames:
        playlist_lines.append([filename, '', 5])

    iview.total_slides = len(playlist_lines)
    iview.slide_num = 0

    if iview.total_slides > 0:
        iview.view(playlist_lines[0][0], 0, playlist_lines, 1)
        # Need to check if the alarm signal is already in use!
        signal.signal(signal.SIGALRM, view_handler)
        signal.alarm(playlist_lines[0][2])

