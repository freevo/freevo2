#
# imenu.py
#
# This is the Freevo image viewer menu module. 
#
# $Id$

import sys
import random
import time, os
import string, popen2, fcntl, select, struct
import rc

# Configuration file. Determines where to look for image files, etc
import config

# Various utilities
import util

# The OSD class, used to communicate with the OSD daemon
import osd

# The menu widget class
import menu

# The Freevo image viewer
import iview

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


osd   = osd.get_singleton()
iview = iview.get_singleton()
rc    = rc.get_singleton()

# remember the position of the selected item in the main menu
main_menu_selected = -1

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
    iview.view(file, number, playlist)


    
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

    for (title, dir) in config.DIR_IMAGES:
        items += [menu.MenuItem(title, cwd, dir, eventhandler, type = 'dir')]

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
        items += [menu.MenuItem(title, cwd, dirname, type = 'dir')]
    
    number = 0

    for file in files:
        title = os.path.splitext(os.path.basename(file))[0]
        m = menu.MenuItem(title, view_image, (file, number, files))

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


