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
DEBUG = 1

TRUE = 1
FALSE = 0


# Create the OSD object
osd = osd.get_singleton()

# Create the ImageViewer object
iview = iview.get_singleton()


#
# view the image
#
def view_image(menuw=None, arg=None):
    osd.clearscreen(color=osd.COL_BLACK)
           
    osd.drawstring('please wait...', osd.width/2 - 60, osd.height/2 - 10,
                   fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
    osd.update()

    file = arg[0]
    number = arg[1]
    playlist = arg[2]
    iview.view(file, number, playlist)


    
#
# The image viewer main menu
#
def main_menu(arg=None, menuw=None):

    items = []

    for (title, dir) in config.DIR_IMAGES:
        items += [menu.MenuItem('[%s]' % title, cwd, dir)]
    
    imagemenu = menu.Menu('IMAGE VIEWER MAIN MENU', items)
    menuw.pushmenu(imagemenu)


#
# The image viewer module change directory handling function
#
def cwd(arg=None, menuw=None):
    dir = arg

    # XXX Now we generate the thumbnails in the skin
    if 0:
        # This could take some time...
        osd.clearscreen(color=osd.COL_BLACK)
        osd.drawstring('please wait...', osd.width/2 - 60, osd.height/2 - 10,
                       fgcolor=osd.COL_ORANGE, bgcolor=osd.COL_BLACK)
        osd.update()
        
    # remove old cache and thumbnail files
    for file in util.match_files(config.FREEVO_CACHEDIR, [ '/image-viewer-[0-9]*' ]):
        os.remove(file)

    dirnames = util.getdirnames(dir)
    files = util.match_files(dir, config.SUFFIX_IMAGE_FILES)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
        items += [menu.MenuItem(title, cwd, dirname)]
    
    number = 0
    print files
    for file in files:
        print file
        title = os.path.splitext(os.path.basename(file))[0]
        m = menu.MenuItem(title, view_image, (file, number, files))

        m.setImage(('photo', file))

        items += [m]

        number += 1

        
    imagemenu = menu.Menu('IMAGE MENU', items)
    menuw.pushmenu(imagemenu)


