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

# The menu widget class
import menu

# The Freevo image viewer
import iview


# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


# Create the ImageViewer object
iview = iview.get_singleton()


#
# view the image
#
def view_image(menuw=None, arg=None):
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

    dirnames = util.getdirnames(dir)
    files = util.match_files(dir, config.SUFFIX_IMAGE_FILES)

    items = []

    for dirname in dirnames:
        title = '[' + os.path.basename(dirname) + ']'
        items += [menu.MenuItem(title, cwd, dirname)]
    
    number = 0
    for file in files:
        title = os.path.basename(file)[:-4]
        items += [menu.MenuItem(title, view_image, (file, number, files))]
        number += 1

    # remove old cache files
    for file in util.match_files(config.FREEVO_CACHEDIR, [ '/image-viewer-[0-9]*.png' ]):
        os.remove(file)
        
    imagemenu = menu.Menu('IMAGE MENU', items)
    menuw.pushmenu(imagemenu)


